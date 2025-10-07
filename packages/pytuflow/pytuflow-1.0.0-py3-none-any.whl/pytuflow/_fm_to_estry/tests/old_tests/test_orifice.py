import unittest
from test_functions import TestFunction


class TestOrifice(unittest.TestCase):

    def test_orifice_orifice(self):
        outpath = 'orifices/out_river_orifice'
        dat = 'orifices/River_Sections_Orifice.dat'
        gxy = 'orifices/River_Sections_Orifice.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_orifice_outfall(self):
        outpath = 'orifices/out_river_outfall'
        dat = 'orifices/River_Sections_Outfall.dat'
        gxy = 'orifices/River_Sections_Outfall.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_orifice_inverted_syphon(self):
        outpath = 'orifices/out_river_inverted_syphon'
        dat = 'orifices/River_Sections_Inverted_Syphon.dat'
        gxy = 'orifices/River_Sections_Inverted_Syphon.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_orifice_flood_relief_arch(self):
        outpath = 'orifices/out_river_flood_relief_arch'
        dat = 'orifices/River_Sections_Flood_Relief_Arch.dat'
        gxy = 'orifices/River_Sections_Flood_Relief_Arch.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)


if __name__ == '__main__':
    unittest.main()
