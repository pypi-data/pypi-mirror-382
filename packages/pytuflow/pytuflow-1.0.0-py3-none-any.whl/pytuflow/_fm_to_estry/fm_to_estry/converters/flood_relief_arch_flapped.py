from fm_to_estry.converters.orifice import Orifice


class FloodReliefArchFlapped(Orifice):

    @staticmethod
    def complete_unit_type_name() -> str:
        return 'FLOOD RELIEF_FLAPPED'
