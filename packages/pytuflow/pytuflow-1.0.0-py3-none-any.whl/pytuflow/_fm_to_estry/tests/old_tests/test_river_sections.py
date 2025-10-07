import unittest
from test_functions import TestFunction


class TestRiverSections(unittest.TestCase):

    def test_river_sections_only(self):
        outpath = 'river_sections/out_river_sections_only'
        dat = 'river_sections/River_Sections_Only.dat'
        gxy = 'river_sections/River_Sections_Only.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_river_with_interpolates(self):
        outpath = 'river_sections/out_river_with_interpolates'
        dat = 'river_sections/River_Sections_w_interpolates.dat'
        gxy = 'river_sections/River_Sections_w_interpolates.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_river_with_replicates(self):
        outpath = 'river_sections/out_river_with_replicates'
        dat = 'river_sections/River_Sections_w_replicates.dat'
        gxy = 'river_sections/River_Sections_w_replicates.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_river_with_junctions(self):
        outpath = 'river_sections/out_river_with_junctions'
        dat = 'river_sections/River_Sections_w_Junctions.dat'
        gxy = 'river_sections/River_Sections_w_Junctions.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)


if __name__ == '__main__':
    unittest.main()
