from fm_to_estry.converters.orifice import Orifice


class FloodReliefArchOpen(Orifice):

    @staticmethod
    def complete_unit_type_name() -> str:
        return 'FLOOD RELIEF_OPEN'
