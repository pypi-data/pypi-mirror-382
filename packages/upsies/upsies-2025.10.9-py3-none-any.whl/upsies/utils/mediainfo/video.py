import collections
import functools
import re

from ... import errors, utils

import logging  # isort:skip
_log = logging.getLogger(__name__)

NO_DEFAULT_VALUE = object()


@functools.cache
def get_width(path, default=NO_DEFAULT_VALUE):
    """
    Return displayed width of video file `path`

    :param str path: Path to video file

        For directories, the return value of :func:`find_main_video` is used.

    :param default: Return value if `path` doesn't exist, raise :exc:`~.ContentError` if not
        provided

    :raise ContentError: if width can't be determined
    """
    try:
        width = utils.mediainfo.lookup(path, ('Video', 'DEFAULT', 'Width'), type=int)
    except errors.ContentError as e:
        if default is NO_DEFAULT_VALUE:
            raise e
        else:
            return default
    else:
        par = utils.mediainfo.lookup(path, ('Video', 'DEFAULT', 'PixelAspectRatio'), type=float, default=1.0)
        if par > 1.0:
            _log.debug('Display width: %r * %r = %r', width, par, width * par)
            width = int(width * par)
        return width


@functools.cache
def get_height(path, default=NO_DEFAULT_VALUE):
    """
    Return displayed height of video file `path`

    :param str path: Path to video file

        For directories, the return value of :func:`find_main_video` is used.

    :param default: Return value if `path` doesn't exist, raise :exc:`~.ContentError` if not
        provided

    :raise ContentError: if height can't be determined
    """
    try:
        height = utils.mediainfo.lookup(path, ('Video', 'DEFAULT', 'Height'), type=int)
    except errors.ContentError as e:
        if default is NO_DEFAULT_VALUE:
            raise e
        else:
            return default
    else:
        par = utils.mediainfo.lookup(path, ('Video', 'DEFAULT', 'PixelAspectRatio'), type=float, default=1.0)
        if par < 1.0:
            _log.debug('Display height: (1 / %r) * %r = %r', par, height, (1 / par) * height)
            height = int((1 / par) * height)
        return height


def get_resolution(path, default=NO_DEFAULT_VALUE):
    """
    Return resolution and scan type of video file `path` as :class:`str` (e.g. "1080p")

    :param str path: Path to video file

        For directories, the return value of :func:`find_main_video` is used.

    :param default: Return value if `path` doesn't exist, raise :exc:`~.ContentError` if not
        provided

    :raise ContentError: if resolution can't be determined
    """
    try:
        resolution = get_resolution_int(path)
        scan_type = get_scan_type(path)
    except errors.ContentError as e:
        if default is NO_DEFAULT_VALUE:
            raise e
        else:
            return default
    else:
        return f'{resolution}{scan_type}'


_standard_resolutions = (
    # (width, height, standard resolution)
    # 4:3
    (640, 480, 480),
    (720, 540, 540),
    (768, 576, 576),
    (960, 720, 720),
    (1440, 1080, 1080),
    (2880, 2160, 2160),
    (5760, 4320, 4320),

    # 16:9
    (853, 480, 480),
    (960, 540, 540),
    (1024, 576, 576),
    (1280, 720, 720),
    (1920, 1080, 1080),
    (3840, 2160, 2160),
    (7680, 4320, 4320),

    # 21:9
    (853, 365, 480),
    (960, 411, 540),
    (1024, 438, 576),
    (1280, 548, 720),
    (1920, 822, 1080),
    (3840, 1645, 2160),
    (7680, 3291, 4320),
)

@functools.cache
def get_resolution_int(path, default=NO_DEFAULT_VALUE):
    """
    Return resolution of video file `path` as :class:`int` (e.g. ``1080``)

    :param str path: Path to video file

        For directories, the return value of :func:`find_main_video` is used.

    :param default: Return value if `path` doesn't exist, raise :exc:`~.ContentError` if not
        provided

    :raise ContentError: if resolution can't be determined
    """
    try:
        actual_width = get_width(path)
        actual_height = get_height(path)
    except errors.ContentError as e:
        if default is NO_DEFAULT_VALUE:
            raise e
        else:
            return default
    else:
        # Find distances from actual display width/height to each standard width/height.
        # Categorize them by standard ratio.
        distances = collections.defaultdict(dict)
        for std_width, std_height, std_resolution in _standard_resolutions:
            std_aspect_ratio = round(std_width / std_height, 1)
            w_dist = abs(std_width - actual_width)
            h_dist = abs(std_height - actual_height)
            resolution = (std_width, std_height, std_resolution)
            distances[std_aspect_ratio][w_dist] = distances[std_aspect_ratio][h_dist] = resolution

        # Find the standard aspect ratio that is closest to the given aspect ratio.
        actual_aspect_ratio = round(actual_width / actual_height, 1)
        std_aspect_ratios = tuple(distances)
        closest_std_aspect_ratio = utils.closest_number(actual_aspect_ratio, std_aspect_ratios)

        # Pick the standard resolution with the lowest distance to the given resolution.
        dists = distances[closest_std_aspect_ratio]
        std_width, std_height, std_resolution = sorted(dists.items())[0][1]

        _log.debug(
            'Closest standard resolution: %r x %r [%.1f] -> %r x %r [%.1f] -> %r',
            actual_width, actual_height, actual_aspect_ratio,
            std_width, std_height, closest_std_aspect_ratio,
            std_resolution,
        )
        return std_resolution


def get_scan_type(path):
    """
    Return scan type of video file `path` ("i" for interlaced, "p" for progressive)

    This always defaults to "p" if it cannot be determined.

    :param str path: Path to video file

        For directories, the return value of :func:`find_main_video` is used.

    :raise ContentError: if scan type can't be determined
    """
    scan_type = utils.mediainfo.lookup(path, ('Video', 'DEFAULT', 'ScanType'), default='p').lower()
    if scan_type in ('interlaced', 'mbaff', 'paff'):
        return 'i'
    else:
        return 'p'


def get_frame_rate(path, default=NO_DEFAULT_VALUE):
    """
    Return frames per second of default video track as :class:`float`

    :param str path: Path to video file

        For directories, the return value of :func:`find_main_video` is used.

    :param default: Return value if `path` doesn't exist, raise :exc:`~.ContentError` if not
        provided

    :raise ContentError: if anything goes wrong
    """
    return utils.mediainfo.lookup(
        path=path,
        keys=('Video', 'DEFAULT', 'FrameRate'),
        default=default,
        type=float,
    )


def get_bit_depth(path, default=NO_DEFAULT_VALUE):
    """
    Return bit depth of default video track (e.g. ``8`` or ``10``)

    :param str path: Path to video file

        For directories, the return value of :func:`find_main_video` is used.

    :param default: Return value if `path` doesn't exist, raise :exc:`~.ContentError` if not
        provided

    :raise ContentError: if anything goes wrong
    """
    return utils.mediainfo.lookup(
        path=path,
        keys=('Video', 'DEFAULT', 'BitDepth'),
        default=default,
        type=int,
    )


known_hdr_formats = {
    'DV',
    'HDR10+',
    'HDR10',
    'HDR',
}
"""Set of valid HDR format names"""

def get_hdr_formats(path, default=NO_DEFAULT_VALUE):
    """
    Return sequence of HDR formats e.g. ``("HDR10",)``, ``("DV", "HDR10")``

    The sequence may be empty.

    :param str path: Path to video file

        For directories, the return value of :func:`find_main_video` is used.

    :param default: Return value if `path` doesn't exist, raise :exc:`~.ContentError` if not
        provided

    :raise ContentError: if anything goes wrong
    """
    def is_dv(video_track):
        return bool(
            # Dolby Vision[ / <more information>]
            re.search(r'^Dolby Vision', video_track.get('HDR_Format', ''))
        )

    def is_hdr10p(video_track):
        return bool(
            # "HDR10+ Profile A" or "HDR10+ Profile B"
            re.search(r'HDR10\+', video_track.get('HDR_Format_Compatibility', ''))
        )

    def is_hdr10(video_track):
        return bool(
            re.search(r'HDR10(?!\+)', video_track.get('HDR_Format_Compatibility', ''))
            or
            re.search(r'BT\.2020', video_track.get('colour_primaries', ''))
        )

    def is_hdr(video_track):
        return bool(
            re.search(r'HDR(?!10)', video_track.get('HDR_Format_Compatibility', ''))
            or
            re.search(r'HDR(?!10)', video_track.get('HDR_Format', ''))
        )

    try:
        video_track = utils.mediainfo.lookup(path, ('Video', 'DEFAULT'))
    except errors.ContentError as e:
        if default is NO_DEFAULT_VALUE:
            raise e
        else:
            return default
    else:
        hdr_formats = []

        # NOTE: DV and HDR(10)(+) can co-exist.
        if is_dv(video_track):
            hdr_formats.append('DV')

        if is_hdr10p(video_track):
            hdr_formats.append('HDR10+')
        elif is_hdr10(video_track):
            hdr_formats.append('HDR10')
        elif is_hdr(video_track):
            hdr_formats.append('HDR')

        return tuple(hdr_formats)


def is_bt601(path, default=NO_DEFAULT_VALUE):
    """
    Whether `path` is BT.601 (~SD) video

    :param str path: Path to video file

        For directories, the return value of :func:`find_main_video` is used.

    :param default: Return value if `path` doesn't exist, raise :exc:`~.ContentError` if not
        provided

    :raise ContentError: if anything goes wrong
    """
    try:
        if (
                _is_color_matrix(path, 'BT.601')
                or _is_color_matrix(path, 'BT.470 System B/G')
        ):
            return True
        else:
            # Assume BT.601 if default video is SD.
            # https://rendezvois.github.io/video/screenshots/programs-choices/#color-matrix
            resolution = get_resolution_int(path)
            return resolution < 720
    except errors.ContentError as e:
        if default is NO_DEFAULT_VALUE:
            raise e
        else:
            return default

def is_bt709(path, default=NO_DEFAULT_VALUE):
    """
    Whether `path` is BT.709 (~UHD) video

    See :func:`is_bt601`.
    """
    return _is_color_matrix(path, 'BT.709', default=default)

def is_bt2020(path, default=NO_DEFAULT_VALUE):
    """
    Whether `path` is BT.2020 (~UHD) video

    See :func:`is_bt601`.
    """
    return _is_color_matrix(path, 'BT.2020', default=default)

def _is_color_matrix(path, matrix, default=NO_DEFAULT_VALUE):
    def normalize_matrix(matrix):
        # Remove whitespace and convert to lower case.
        return ''.join(matrix.casefold().split())

    matrix = normalize_matrix(matrix)

    try:
        video_tracks = utils.mediainfo.lookup(path, ('Video',))
    except errors.ContentError as e:
        if default is NO_DEFAULT_VALUE:
            raise e
        else:
            return default
    else:
        # https://rendezvois.github.io/video/screenshots/programs-choices/#color-matrix
        for track in video_tracks:
            if normalize_matrix(track.get('matrix_coefficients', '')).startswith(matrix):
                return True
        return False


_video_translations = (
    ('x264', {'Encoded_Library_Name': re.compile(r'^x264$')}),
    ('x265', {'Encoded_Library_Name': re.compile(r'^x265$')}),
    ('XviD', {'Encoded_Library_Name': re.compile(r'^XviD$')}),
    ('H.264', {'Format': re.compile(r'^AVC$')}),
    ('H.265', {'Format': re.compile(r'^HEVC$')}),
    ('VP9', {'Format': re.compile(r'^VP9$')}),
    ('VC-1', {'Format': re.compile(r'^VC-1$')}),
    ('MPEG-2', {'Format': re.compile(r'^MPEG Video$')}),
)

@functools.cache
def get_video_format(path, default=NO_DEFAULT_VALUE):
    """
    Return video format of default video track

    Return x264, x265 or XviD if either one is detected.

    :param str path: Path to video file

        For directories, the return value of :func:`find_main_video` is used.

    :param default: Return value if `path` doesn't exist or video format cannot be determined, raise
        :exc:`~.ContentError` if not provided

    :raise ContentError: if anything goes wrong
    """
    try:
        video_track = utils.mediainfo.lookup(path, ('Video', 'DEFAULT'))
    except errors.ContentError as e:
        if default is NO_DEFAULT_VALUE:
            raise e
        else:
            return default
    else:
        for vfmt, regexs in _video_translations:
            for key, regex in regexs.items():
                value = video_track.get(key)
                if value and regex.search(value):
                    _log.debug('Detected video format: %s', vfmt)
                    return vfmt

        if default is NO_DEFAULT_VALUE:
            raise errors.ContentError('Unable to detect video format')
        else:
            _log.debug('Failed to detect video format, falling back to default: %s', default)
            return default
