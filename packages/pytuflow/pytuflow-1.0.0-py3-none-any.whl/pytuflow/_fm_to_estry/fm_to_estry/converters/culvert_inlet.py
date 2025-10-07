from fm_to_estry.converters.converter import Converter


class CulvertInlet(Converter):
    """Actual conversion is considered elsewhere, the presence of this class
    just means it gets counted as 'converted'"""

    @staticmethod
    def complete_unit_type_name() -> str:
        return 'CULVERT_INLET'
