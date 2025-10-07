from fm_to_estry.converters.orifice import Orifice


class InvertedSyphonOpen(Orifice):

    @staticmethod
    def complete_unit_type_name() -> str:
        return 'INVERTED SYPHON_OPEN'
