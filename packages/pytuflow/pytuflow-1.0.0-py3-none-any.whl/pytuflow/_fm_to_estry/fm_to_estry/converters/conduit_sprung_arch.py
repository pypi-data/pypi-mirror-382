import typing

import pandas as pd

from fm_to_estry.helpers.geometry import parabolic_arch_conduit, create_hw_table
from .conduit_full_arch import ConduitFullArch


if typing.TYPE_CHECKING:
    from fm_to_estry.parsers.units.handler import Handler


class ConduitSprungArch(ConduitFullArch):

    @staticmethod
    def complete_unit_type_name() -> str:
        return 'CONDUIT_SPRUNGARCH'

    def arch_hw_table(self, unit: 'Handler') -> pd.DataFrame:
        base = pd.DataFrame([
            [0., unit.inv + unit.sprhyt, unit.frisid],
            [0., unit.inv, unit.fribot],
            [unit.width, unit.inv, unit.fribot],
            [unit.width, unit.inv + unit.sprhyt, unit.frisid]
        ], columns=['x', 'z', 'n'])
        arch = parabolic_arch_conduit(
            unit.width, unit.inv + unit.sprhyt + unit.archyt, unit.inv + unit.sprhyt,
            as_df=True
        )
        arch['n'] = unit.friarc
        section = pd.concat([base, arch[::-1]], axis=0)
        return create_hw_table(section, as_df=True)
