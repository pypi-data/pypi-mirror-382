import unittest
from test_functions import TestFunction


class TestCulvert(unittest.TestCase):

    def test_culverts(self):
        outpath = 'culverts/out_river_sections_culvert'
        dat = 'culverts/River_Sections_Culvert_inlet_outlet.dat'
        gxy = 'culverts/River_Sections_Culvert_inlet_outlet.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)


if __name__ == '__main__':
    unittest.main()
