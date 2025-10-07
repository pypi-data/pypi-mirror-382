import unittest
from test_functions import TestFunction


class TestConduits(unittest.TestCase):

    def test_conduits_circular(self):
        outpath = 'conduits/out_river_sections_with_circular_conduits'
        dat = 'conduits/River_Sections_w_Circular_Conduit.dat'
        gxy = 'conduits/River_Sections_w_Circular_Conduit.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_conduits_rectangular(self):
        outpath = 'conduits/out_river_sections_with_rectangular_conduits'
        dat = 'conduits/River_Sections_w_Rectangular_Conduit.dat'
        gxy = 'conduits/River_Sections_w_Rectangular_Conduit.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_conduits_symmetrical(self):
        outpath = 'conduits/out_river_sections_with_symmetrical_conduits'
        dat = 'conduits/River_Sections_w_Symmetrical_Conduit.dat'
        gxy = 'conduits/River_Sections_w_Symmetrical_Conduit.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_conduits_asymmetrical(self):
        outpath = 'conduits/out_river_sections_with_asymmetrical_conduits'
        dat = 'conduits/River_Sections_w_Asymmetrical_Conduit.dat'
        gxy = 'conduits/River_Sections_w_Asymmetrical_Conduit.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_conduits_full_arch(self):
        outpath = 'conduits/out_river_sections_with_full_arch_conduit'
        dat = 'conduits/River_Sections_w_Full_Arch_Conduit.dat'
        gxy = 'conduits/River_Sections_w_Full_Arch_Conduit.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_conduits_sprung_arch(self):
        outpath = 'conduits/out_river_sections_with_sprung_arch_conduit'
        dat = 'conduits/River_Sections_w_Sprung_Arch_Conduit.dat'
        gxy = 'conduits/River_Sections_w_Sprung_Arch_Conduit.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)


if __name__ == '__main__':
    unittest.main()
