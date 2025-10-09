"""
Concrete :class:`~.TrackerConfigBase` subclass for ANT
"""

import base64

from ... import utils
from .. import base


class AntTrackerConfig(base.TrackerConfigBase):
    base_url: base.config.base_url(
        base64.b64decode('aHR0cHM6Ly9hbnRoZWxpb24ubWU=').decode('ascii')
    )

    apikey: base.config.apikey('')

    announce_url: base.config.announce_url('', autofetched=False)

    anonymous: base.config.anonymous('no')

    exclude: base.config.exclude(
        base.exclude_regexes.checksums,
        base.exclude_regexes.images,
        base.exclude_regexes.nfo,
        base.exclude_regexes.samples,
    )


cli_arguments = {
    'submit': {
        ('--anonymous', '--an'): {
            'help': 'Hide your username for this submission',
            'action': 'store_true',
            # This must be `None` so it doesn't override the "anonymous" value from the config file.
            # See CommandBase.get_options().
            'default': None,
        },
        ('--nfo',): {
            'help': 'Path to NFO file (supersedes any *.nfo file found in the release directory)',
        },
        ('--tmdb', '--tm'): {
            'help': 'TMDb ID or URL',
            'type': utils.argtypes.webdb_id('tmdb'),
        },
    },
}
