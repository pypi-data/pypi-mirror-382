import unittest
from test_functions import TestFunction


class TestSluice(unittest.TestCase):

    def test_sluice_vertical_non_operational(self):
        outpath = 'sluice_gates/out_river_sections_vertical_sluice'
        dat = 'sluice_gates/River_Sections_Vertical.dat'
        gxy = 'sluice_gates/River_Sections_Vertical.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)


if __name__ == '__main__':
    unittest.main()
