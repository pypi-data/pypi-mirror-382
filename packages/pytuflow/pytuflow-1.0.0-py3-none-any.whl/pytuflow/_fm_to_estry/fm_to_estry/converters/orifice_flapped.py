from fm_to_estry.converters.orifice import Orifice


class OrificeFlapped(Orifice):

    @staticmethod
    def complete_unit_type_name() -> str:
        return 'ORIFICE_FLAPPED'
