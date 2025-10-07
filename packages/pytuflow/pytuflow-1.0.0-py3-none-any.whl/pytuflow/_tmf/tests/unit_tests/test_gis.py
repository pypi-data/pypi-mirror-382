from tmf.tuflow_model_files.gis import tuflow_type_requires_feature_iter, gdal_projection
from tmf.tuflow_model_files.file import TuflowPath


def test_gdal_projection():
    p = TuflowPath(r'./tests/unit_tests/test_datasets/models/shp/model/grid/DEM_SI_Unit_01.flt')
    srs = gdal_projection(p)
