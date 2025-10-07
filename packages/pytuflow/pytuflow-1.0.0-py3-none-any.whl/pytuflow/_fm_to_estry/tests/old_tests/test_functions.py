import sys
import unittest
import numpy as np
from pathlib import Path
from fm_to_estry.helpers.gis import get_epsg_from_file, vector_geometry_as_array, layer_attributes
from fm_to_estry import main


class TestFunction(unittest.TestCase):

    def run_output_test(self, dat, gxy, outpath):
        # delete any previous output files
        path = Path(outpath)
        for p in path.glob('*.*'):
            p.unlink()

        sys.argv = [
            'python',
            dat,
            gxy,
            '-crs', '32760',
            '-out', outpath
        ]
        main()

        # csv comparison
        for p_chk in (path / 'chk').glob('*.csv'):
            found = False
            for p in path.glob('*.csv'):
                if p.name == p_chk.name:
                    found = True
                    with p.open('r') as f1:
                        with p_chk.open('r') as f2:
                            # header
                            self.assertEqual(f1.readline(), f2.readline())
                            # values
                            a1 = np.genfromtxt(f1, dtype=np.float64, delimiter=',')
                            a2 = np.genfromtxt(f2, dtype=np.float64, delimiter=',')
                            self.assertTrue(np.allclose(a1, a2, equal_nan=True))
            self.assertTrue(found)

        # GIS comparison
        for p_chk in (path / 'chk').glob('*.shp'):
            found = False
            for p in path.glob('*.shp'):
                if p.name == p_chk.name:
                    found = True
                    f1 = str(p.resolve())
                    f2 = str(p_chk.resolve())
                    # epsg
                    self.assertEqual(get_epsg_from_file(f1), get_epsg_from_file(f1))
                    # geometry
                    self.assertTrue(np.allclose(vector_geometry_as_array(f1), vector_geometry_as_array(f2), equal_nan=True))
                    # attributes
                    self.assertEqual(layer_attributes(f1), layer_attributes(f2))
            self.assertTrue(found)
