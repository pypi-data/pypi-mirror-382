import typing
from collections import OrderedDict

from fm_to_estry.converters.weir import Weir


if typing.TYPE_CHECKING:
    from fm_to_estry.parsers.units.handler import Handler


class Crump(Weir):

    @staticmethod
    def complete_unit_type_name() -> str:
        return 'CRUMP_'

    def map_nwk_attributes(self, field_map: dict, unit: 'Handler') -> OrderedDict:
        d = super().map_nwk_attributes(field_map, unit)
        d['Type'] = 'WC'
        d['Height_or_WF'] = unit.cc
        return d
