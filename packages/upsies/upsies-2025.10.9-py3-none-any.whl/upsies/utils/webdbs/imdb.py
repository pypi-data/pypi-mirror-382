"""
API for imdb.com
"""

import functools
import json
import re

import async_lru

from ... import utils
from ..types import ReleaseType
from . import common
from .base import WebDbApiBase

import logging  # isort:skip
_log = logging.getLogger(__name__)


class ImdbApi(WebDbApiBase):
    """API for imdb.com"""

    name = 'imdb'
    label = 'IMDb'

    default_config = {}

    _url_base = 'https://www.imdb.com'
    _soup_cache = {}

    async def _get_soup(self, path, params={}):
        path = path.rstrip('/')

        cache_id = (path, tuple(sorted(params.items())))
        if cache_id in self._soup_cache:
            return self._soup_cache[cache_id]

        text = await utils.http.get(
            url=f'{self._url_base}/{path}/',
            params=params,
            user_agent=await utils.http.get_popular_user_agent(),
            cache=True,
        )

        self._soup_cache[cache_id] = utils.html.parse(text)
        return self._soup_cache[cache_id]

    _title_types = {
        ReleaseType.movie: 'feature,tv_movie,short,video,tv_short',
        ReleaseType.season: 'tv_series,tv_miniseries',
        # Searching for single episodes is currently not supported
        ReleaseType.episode: 'tv_series,tv_miniseries',
    }

    def sanitize_query(self, query):
        """
        Deal with IMDb-specific quirks

        - Remove ``"and"`` from :attr:`.Query.title` because IMDb doesn't find
          ``"Foo & Bar"`` if we search for ``"Foo and Bar"``. It's seems to work
          vice versa, i.e. the query ``"Foo and Bar"`` finds ``"Foo & Bar"``, so
          we keep any ``"&"``.

        - Replace ``"dont"`` with ``"don't"``, ``"cant"`` with ``"can't"``.
        """
        query = super().sanitize_query(query)
        query.title = re.sub(r'\s(?i:and)(\s)', r'\1', query.title)
        query.title = re.sub(r'\b(?i:dont)(\b)', "don't", query.title)
        query.title = re.sub(r'\b(?i:cant)(\b)', "can't", query.title)
        query.title = re.sub(r'\b(?i:wont)(\b)', "won't", query.title)
        return query

    def get_id_from_text(self, text):
        # Example: https://www.imdb.com/title/tt0048918/
        match = re.search(r'\b(tt\d+)\b', text)
        if match:
            return match.group(1)

    async def search(self, query):
        _log.debug('Searching IMDb for %s', query)

        if query.id:
            title_english = await self.title_english(query.id)
            title_original = await self.title_original(query.id)
            return [_ImdbSearchResult(
                imdb_api=self,
                cast=functools.partial(self.cast, query.id),
                countries=functools.partial(self.countries, query.id),
                directors=functools.partial(self.directors, query.id),
                genres=functools.partial(self.genres, query.id),
                id=query.id,
                summary=functools.partial(self.summary, query.id),
                title=title_english or title_original,
                title_english=title_english,
                title_original=title_original,
                type=await self.type(query.id),
                url=await self.url(query.id),
                year=await self.year(query.id),
            )]

        elif not query.title:
            return []

        else:
            path = 'search/title/'
            params = {'title': query.title_normalized if not query.id else query.id}
            if query.type is not ReleaseType.unknown:
                params['title_type'] = self._title_types[query.type]
            if query.year is not None:
                params['release_date'] = f'{query.year}-01-01,{query.year}-12-31'

            def is_search_result(tag):
                return 'ipc-metadata-list-summary-item__tc' in tag.get('class', ())

            soup = await self._get_soup(path, params=params)
            items = soup.find_all(is_search_result)
            results = [
                _ImdbSearchResult(soup=item, imdb_api=self)
                for item in items
            ]
            return results

    _person_url_path_regex = re.compile(r'(/name/nm\d+)')

    @async_lru.alru_cache
    async def _get_json(self, id, key=None, default=None):
        soup = await self._get_soup(f'title/{id}/')
        tag = soup.find('script', type='application/ld+json')
        dct = json.loads(tag.string)
        if dct:
            if key is None:
                return dct
            elif key in dct:
                return dct[key]
        return default

    async def _get_persons(self, id, type):
        infos = await self._get_json(id, key=type, default=())
        return tuple(
            common.Person(utils.html.parse(info['name']), url=info['url'].rstrip('/'))
            for info in infos
            if info['@type'] == 'Person'
        )

    async def cast(self, id):
        if id:
            return await self._get_persons(id, type='actor')
        return ()

    async def _countries(self, id):
        countries = []
        if id:
            soup = await self._get_soup(f'title/{id}/')
            a_tags = soup.find_all(href=re.compile(r'/search/title.*?country_of_origin='))
            for a_tag in a_tags:
                country = ''.join(a_tag.stripped_strings)
                countries.append(country)
        return tuple(countries)

    _creators_label_regex = re.compile('^Creators?:?$')

    async def creators(self, id):
        if id:
            return await self._get_persons(id, type='creator')
        return ()

    _directors_label_regex = re.compile('^Directors?:?$')

    async def directors(self, id):
        if id:
            return await self._get_persons(id, type='director')
        return ()

    async def genres(self, id):
        if id:
            genres = await self._get_json(id, key='genre', default=())
            return tuple(
                genre.casefold()
                for genre in genres
            )
        return ()

    async def poster_url(self, id, season=None):
        if id:
            poster_url = await self._get_json(id, key='image', default='')
            # Request scaled down poster (300 pixels wide)
            poster_url = re.sub(r'._V1_*.jpg$', '._V1_SX300.jpg', poster_url)
            return poster_url

        return ''

    rating_min = 0.0
    rating_max = 10.0

    async def rating(self, id):
        if id:
            info = await self._get_json(id, key='aggregateRating')
            if info:
                return info.get('ratingValue', None)
        return None

    _ignored_runtimes_keys = (
        re.compile(r'^(?i:approx)\w*$'),
    )

    async def _runtimes(self, id):
        if id:
            soup = await self._get_soup(f'title/{id}/technical')
            label_tags = soup.select('.ipc-metadata-list__item > .ipc-metadata-list-item__label')
            for tag in label_tags:
                if 'Runtime' in utils.html.as_text(tag):
                    values_tag = tag.next_sibling
                    if values_tag:
                        return self._parse_runtimes(values_tag)
        return {}

    def _parse_runtimes(self, tag):
        runtimes = {}
        for li_tag in tag.find_all('li'):
            li_text = ' '.join(li_tag.stripped_strings)

            # Examples: 2h 13m (133 min)
            #           2h 28m (148 min) (extended) (United States)
            #           2h 42m (162 min) 3h 6m (186 min) (director's cut) 3h 35m (215 min) (Ultimate Cut)
            #           55m
            match = re.search(r'\((\d+)\s*(?:min|m)\)\s*(?:\((.+?)\)|)', li_text)
            if not match:
                match = re.search(r'^(\d+)\s*(?:min|m)$', li_text)

            if match:
                groups = match.groups()
                minutes = int(groups[0])
                if len(groups) >= 2:
                    key = utils.string.capitalize(groups[1]) if groups[1] else 'default'
                else:
                    key = 'default'

                if not any(regex.search(key) for regex in self._ignored_runtimes_keys):
                    runtimes[key] = minutes

        return runtimes

    async def summary(self, id):
        if id:
            description = await self._get_json(id, key='description', default='')
            if not description.endswith('...'):
                return description

            # Try to find the complete description in the trailer section.
            trailer = await self._get_json(id, key='trailer')
            if trailer:
                description = trailer.get('description', '')
                if not description.endswith('...'):
                    return description

        return ''

    async def _title_original(self, id):
        # /title/tt.../releaseinfo/#akas: Find "(original title)" row in table
        # Example: https://www.imdb.com/title/tt1405737/releaseinfo/#akas
        soup = await self._get_soup(f'title/{id}/releaseinfo')
        for tag in soup.select('.ipc-metadata-list__item > .ipc-metadata-list-item__label'):
            text = utils.html.as_text(tag)
            if 'original' in text:
                return utils.html.as_text(tag.next_sibling)

        return ''

    async def _titles_english(self, id):
        soup = await self._get_soup(f'title/{id}/releaseinfo')

        # Get the main (usually English) title from the <head>
        tag = soup.select_one('head meta[property="og:title"]')
        if tag:
            match = re.search(r'^(.*)\s+\(.*?\)\s*', tag['content'])
            if match:
                return [match.group(1).strip()]

        return ['']

    async def type(self, id):
        if id:
            typ = await self._get_json(id, key='@type')
            if typ == 'Movie':
                return ReleaseType.movie
            elif typ == 'TVSeries':
                return ReleaseType.season
            elif typ == 'TVEpisode':
                return ReleaseType.episode

        return ReleaseType.unknown

    async def url(self, id):
        if id:
            return f'{self._url_base.rstrip("/")}/title/{id}'
        return ''

    async def year(self, id):
        if id:
            soup = await self._get_soup(f'title/{id}/releaseinfo')
            for tag in soup.find_all(class_="ipc-metadata-list-item__list-content-item"):
                text = ' '.join(reversed(tuple(tag.stripped_strings))).lower()
                match = re.search(r'\b(\d{4})\b', text)
                if match:
                    return match.group(1)
        return ''


class _ImdbSearchResult(common.SearchResult):
    def __init__(self, *, imdb_api, soup=None, cast=None, countries=None,
                 directors=None, genres=None, id=None, poster=None, summary=None, title=None,
                 title_english=None, title_original=None, type=None, url=None,
                 year=None):
        self._imdb_api = imdb_api
        soup = soup or utils.html.parse('')
        id = id or self._get_id(soup)
        super().__init__(
            cast=cast or functools.partial(imdb_api.cast, id),
            countries=countries or functools.partial(imdb_api.countries, id),
            directors=directors or functools.partial(imdb_api.directors, id),
            genres=genres or functools.partial(imdb_api.genres, id),
            id=id or self._get_id(soup),
            poster=functools.partial(imdb_api.poster, id),
            summary=summary or self._get_summary(soup),
            title=title or self._get_title(soup),
            title_english=title_english or functools.partial(imdb_api.title_english, id),
            title_original=title_original or functools.partial(imdb_api.title_original, id),
            type=type or self._get_type(soup),
            url=url or self._get_url(soup),
            year=year or self._get_year(soup),
        )

    def _get_id(self, soup):
        a_tag = soup.find('a')
        if a_tag:
            href = a_tag.get('href')
            return re.sub(r'^.*/([t0-9]+)/.*$', r'\1', href)
        return ''

    def _get_summary(self, soup):
        summary = ''
        tag = soup.find('div', attrs={'class': 'ipc-html-content', 'role': 'presentation'})
        if tag:
            return tag.string.strip()

        return summary

    def _get_title(self, soup):
        tag = soup.find(attrs={'class': 'ipc-title__text'})
        if tag:
            title = tag.string.strip()
            # Search result number is prepended to title
            title = re.sub(r'^\d+\.', '', title)
            return title.strip()

        return ''

    def _get_type(self, soup):
        tag = soup.find(attrs={'class': 'dli-title-type-data'})
        if tag:
            text = tag.string.strip().lower()
            if any(name in text for name in ('movie', 'video', 'short')):
                return ReleaseType.movie
            elif 'series' in text:
                return ReleaseType.series

        # Sometimes there is no indication of type in search results. It seems
        # this only happens to movies.
        return ReleaseType.movie

    def _get_url(self, soup):
        id = self._get_id(soup)
        if id:
            return f'{ImdbApi._url_base}/title/{id}'
        return ''

    def _get_year(self, soup):
        # New website design
        # Find the first four-digit number. This covers movies as well as series
        # in "YYYY-YYYY" and "YYYY-" format.
        year_regex = re.compile(r'(\d{4})')
        tags = soup.find_all(attrs={'class': 'dli-title-metadata-item'})
        for tag in tags:
            text = tag.string.strip()
            match = year_regex.search(text)
            if match:
                year = match.group(1)
                return year

        return ''
