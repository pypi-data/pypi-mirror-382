import unittest
from test_functions import TestFunction


class TestWiers(unittest.TestCase):

    def test_weirs_broad_crested(self):
        outpath = 'weirs/out_river_sections_broad_crested_weir'
        dat = 'weirs/River_Sections_Broad_Crested_Weir.dat'
        gxy = 'weirs/River_Sections_Broad_Crested_Weir.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_weirs_crump(self):
        outpath = 'weirs/out_river_sections_crump_weir'
        dat = 'weirs/River_Sections_Crump_Weir.dat'
        gxy = 'weirs/River_Sections_Crump_Weir.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_weirs_flow_head(self):
        outpath = 'weirs/out_river_sections_flow_head_weir'
        dat = 'weirs/River_Sections_Flow_Head_Weir.dat'
        gxy = 'weirs/River_Sections_Flow_Head_Weir.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_weirs_gated(self):
        outpath = 'weirs/out_river_sections_gated_weir'
        dat = 'weirs/River_Sections_Gated_weir.dat'
        gxy = 'weirs/River_Sections_Gated_weir.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_weirs(self):
        outpath = 'weirs/out_river_sections_general_weir'
        dat = 'weirs/River_Sections_General_weir.dat'
        gxy = 'weirs/River_Sections_General_weir.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_weirs_labyrinth(self):
        outpath = 'weirs/out_river_sections_labyrinth_weir'
        dat = 'weirs/River_Sections_Labyrinth_weir.dat'
        gxy = 'weirs/River_Sections_Labyrinth_weir.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_weirs_notional(self):
        outpath = 'weirs/out_river_sections_notional_weir'
        dat = 'weirs/River_Sections_Notional_weir.dat'
        gxy = 'weirs/River_Sections_Notional_weir.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_weirs_sharp_crested(self):
        outpath = 'weirs/out_river_sections_sharp_crested_weir'
        dat = 'weirs/River_Sections_Sharp_Crested_weir.dat'
        gxy = 'weirs/River_Sections_Sharp_Crested_weir.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_weirs_spill(self):
        outpath = 'weirs/out_river_sections_inline_spill'
        dat = 'weirs/River_Sections_InLine_Spill.dat'
        gxy = 'weirs/River_Sections_InLine_Spill.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)


if __name__ == '__main__':
    unittest.main()
