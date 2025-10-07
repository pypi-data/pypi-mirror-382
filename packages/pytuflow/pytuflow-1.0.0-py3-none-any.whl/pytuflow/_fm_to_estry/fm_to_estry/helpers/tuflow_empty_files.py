from collections import OrderedDict
from osgeo import ogr


def tuflow_empty_field_map(empty_type: str) -> OrderedDict:
    """
    Return empty field type for the given empty type.

    :param empty_type: str
    :return: OrderedDict
    """

    if empty_type.lower() == '1d_nwk':
        return _1d_nwk_empty()
    elif empty_type.lower() == '1d_tab':
        return _1d_tab_empty()


def _1d_tab_empty() -> OrderedDict:
    """
    1d_tab empty type fields.

    :return: OrderedDict
    """

    fields = OrderedDict(
        {
            'Source': {'type': ogr.OFTString, 'width': 50},
            'Type': {'type': ogr.OFTString, 'width': 2},
            'Flags': {'type': ogr.OFTString, 'width': 8},
            'Column_1': {'type': ogr.OFTString, 'width': 20},
            'Column_2': {'type': ogr.OFTString, 'width': 20},
            'Column_3': {'type': ogr.OFTString, 'width': 20},
            'Column_4': {'type': ogr.OFTString, 'width': 20},
            'Column_5': {'type': ogr.OFTString, 'width': 20},
            'Column_6': {'type': ogr.OFTString, 'width': 20},
            'Z_Increment': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'Z_Maximum': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'Skew': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'Comment_1': {'type': ogr.OFTString, 'width': 100},
            'Comment_2': {'type': ogr.OFTString, 'width': 100}
        }
    )

    return fields


def _1d_nwk_empty() -> OrderedDict:
    """
    1d_nwk empty type fields.

    :return: OrderedDict
    """

    fields = OrderedDict(
        {
            'ID': {'type': ogr.OFTString, 'width': 36},
            'Type': {'type': ogr.OFTString, 'width': 36},
            'Ignore': {'type': ogr.OFTString, 'width': 1},
            'UCS': {'type': ogr.OFTString, 'width': 1},
            'Len_or_ANA': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'n_nf_Cd': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'US_Invert': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'DS_Invert': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'Form_Loss': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'pBlockage': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'Inlet_Type': {'type': ogr.OFTString, 'width': 256},
            'Conn_1D_2D': {'type': ogr.OFTString, 'width': 4},
            'Conn_No': {'type': ogr.OFTInteger, 'width': 8},
            'Width_or_Dia': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'Height_or_WF': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'Number_of': {'type': ogr.OFTInteger, 'width': 8},
            'HConF_or_WC': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'WConF_or_WEx': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'EntryC_or_WSa': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
            'ExitC_or_WSb': {'type': ogr.OFTReal, 'width': 15, 'prec': 5},
        }
    )

    return fields
