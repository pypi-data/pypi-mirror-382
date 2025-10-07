import unittest
from test_functions import TestFunction


class TestBridges(unittest.TestCase):

    def test_bridge_pier_loss(self):
        outpath = 'bridges/out_river_sections_w_pier_loss_bridge'
        dat = 'bridges/River_Sections_w_Pier_Loss_Bridge.dat'
        gxy = 'bridges/River_Sections_w_Pier_Loss_Bridge.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_bridge_usbpr(self):
        outpath = 'bridges/out_river_sections_w_usbpr_bridge'
        dat = 'bridges/River_Sections_w_USBPR_Bridge.dat'
        gxy = 'bridges/River_Sections_w_USBPR_Bridge.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_bridge_arch(self):
        outpath = 'bridges/out_river_sections_w_arch_bridge'
        dat = 'bridges/River_Sections_w_Arch_Bridge.dat'
        gxy = 'bridges/River_Sections_w_Arch_Bridge.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)

    def test_bridge_arch_with_spill(self):
        outpath = 'bridges/out_river_sections_w_arch_bridge_wspill'
        dat = 'bridges/River_Sections_w_Arch_Bridge_wSpill.dat'
        gxy = 'bridges/River_Sections_w_Arch_Bridge_wSpill.gxy'
        test = TestFunction()
        test.run_output_test(dat, gxy, outpath)


if __name__ == '__main__':
    unittest.main()
