from fm_to_estry.converters.orifice import Orifice


class OutfallFlapped(Orifice):

    @staticmethod
    def complete_unit_type_name() -> str:
        return 'OUTFALL_FLAPPED'
