from fm_to_estry.converters.orifice import Orifice


class OutfallOpen(Orifice):

    @staticmethod
    def complete_unit_type_name() -> str:
        return 'OUTFALL_OPEN'
