from pathlib import Path

import numpy as np
from osgeo import ogr

from fm_to_estry.helpers.gis import get_driver_name_from_extension


def vector_geom_as_array(lyr):
    feats = []
    max_npoints = 0
    for feature in lyr:
        geom = feature.GetGeometryRef()
        max_npoints = max(geom.GetPointCount(), max_npoints)
        feats.append(geom.GetPoints())

    for i, feat in enumerate(feats):
        if len(feat) < max_npoints:
            f = list(feat) + [(np.nan, np.nan) for x in range(max_npoints - len(feat))]
            feats[i] = tuple(f)

    return np.array(feats)


def vector_attributes(lyr):
    feats = []
    for feature in lyr:
        feats.append([feature.GetFieldAsString(i) for i in range(feature.GetFieldCount())])

    return feats


class VectorLayer:
    """Class with context manager so layers are closed properly and easily."""

    def __init__(self, fpath) -> None:
        self.fpath = str(fpath)
        self.open_lyr = False
        if '>>' in self.fpath:
            self.open_lyr = True
            self.dbpath, self.lyrname = self.fpath.split(' >> ')
        else:
            self.dbpath = self.fpath
        self.driver_name = None
        self.ds = None
        self.lyr = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        self.driver_name = get_driver_name_from_extension('vector', Path(self.dbpath).suffix)
        self.ds = ogr.GetDriverByName(self.driver_name).Open(self.dbpath)
        if self.open_lyr:
            self.lyr = self.ds.GetLayer(self.lyrname)

    def close(self):
        self.ds, self.lyr = None, None

    def layers(self):
        for i in range(self.ds.GetLayerCount()):
            yield self.ds.GetLayerByIndex(i).GetName()
