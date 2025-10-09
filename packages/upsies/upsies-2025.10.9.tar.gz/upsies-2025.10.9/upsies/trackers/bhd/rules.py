from ... import errors
from ..base import rules


class BhdHdOnly(rules.HdOnly):
    pass


class BhdBannedGroup(rules.BannedGroup):

    banned_groups = {
        '4K4U',
        'AOC',
        'C4K',
        'd3g',
        'EASports',
        'FGT',  # Unless no other encode is available.
        'MeGusta',
        'MezRips',
        'nikt0',
        'ProRes',
        'RARBG',
        'ReaLHD',
        'SasukeducK',
        'Sicario',
        'TEKNO3D',  # They have requested their torrents are not shared off site.
        'Telly',
        'tigole',
        'TOMMY',
        'WKS',
        'x0r',
        'YIFY',
        'CRUCiBLE',
    }

    async def _check_custom(self):
        # No iFT remuxes.
        if (
                self.is_group('iFT')
                and 'Remux' in self.release_name.source
        ):
            raise errors.BannedGroup('iFT', additional_info='No remuxes from iFT')

        # No EVO encodes. WEB-DLs are fine.
        if (
                self.is_group('EVO')
                and 'WEB' not in self.release_name.source
        ):
            raise errors.BannedGroup('EVO', additional_info='No encodes, only WEB-DL')
