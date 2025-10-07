from unittest import TestCase

from fm_to_estry.converters.converter import Converter
from fm_to_estry.parsers.dat import DAT
from fm_to_estry.parsers.gxy import GXY
from fm_to_estry.utils.output_writer import OutputWriter


class TestConverter(TestCase):

    def test_river(self):
        datpath = './tests/data/River_Sections_Only.dat'
        gxypath = './tests/data/River_Sections_Only.gxy'
        dat = DAT(datpath)
        gxy = GXY(gxypath)
        dat.add_gxy(gxy)
        unit = dat.unit('RIVER_SECTION_US_1')
        output = unit.convert()
        self.assertEqual(1, 1)

    def test_conduit_circular(self):
        datpath = './tests/data/River_Sections_w_Circular_Conduit.dat'
        gxypath = './tests/data/River_Sections_w_Circular_Conduit.gxy'
        dat = DAT(datpath)
        gxy = GXY(gxypath)
        dat.add_gxy(gxy)
        unit = dat.unit('CONDUIT_CIRCULAR_DS_1a')
        output = unit.convert()
        self.assertEqual(1, 1)

    def test_conduit_rectangular(self):
        datpath = './tests/data/River_Sections_w_Rectangular_Conduit.dat'
        gxypath = './tests/data/River_Sections_w_Rectangular_Conduit.gxy'
        dat = DAT(datpath)
        gxy = GXY(gxypath)
        dat.add_gxy(gxy)
        unit = dat.unit('CONDUIT_RECTANGULAR_DS_1a')
        output = unit.convert()
        self.assertEqual(1, 1)

    def test_conduit_symmetrical(self):
        datpath = './tests/data/River_Sections_w_Symmetrical_Conduit.dat'
        gxypath = './tests/data/River_Sections_w_Symmetrical_Conduit.gxy'
        dat = DAT(datpath)
        gxy = GXY(gxypath)
        dat.add_gxy(gxy)
        unit = dat.unit('CONDUIT_SECTION_DS_1a')
        output = unit.convert()
        self.assertEqual(1, 1)

    def test_conduit_asymmetrical(self):
        datpath = './tests/data/River_Sections_w_Asymmetrical_Conduit.dat'
        gxypath = './tests/data/River_Sections_w_Asymmetrical_Conduit.gxy'
        dat = DAT(datpath)
        gxy = GXY(gxypath)
        dat.add_gxy(gxy)
        unit = dat.unit('CONDUIT_ASYMMETRIC_DS_1a')
        output = unit.convert()
        self.assertEqual(1, 1)

    def test_conduit_full_arch(self):
        datpath = './tests/data/River_Sections_w_Full_Arch_Conduit.dat'
        gxypath = './tests/data/River_Sections_w_Full_Arch_Conduit.gxy'
        dat = DAT(datpath)
        gxy = GXY(gxypath)
        dat.add_gxy(gxy)
        unit = dat.unit('CONDUIT_FULLARCH_DS_1a')
        output = unit.convert()
        self.assertEqual(1, 1)

    def test_conduit_sprung_arch(self):
        datpath = './tests/data/River_Sections_w_Sprung_Arch_Conduit.dat'
        gxypath = './tests/data/River_Sections_w_Sprung_Arch_Conduit.gxy'
        dat = DAT(datpath)
        gxy = GXY(gxypath)
        dat.add_gxy(gxy)
        unit = dat.unit('CONDUIT_SPRUNGARCH_DS_1a')
        output = unit.convert()
        self.assertEqual(1, 1)

    def test_conduit_replicate(self):
        datpath = './tests/data/River_Sections_w_replicates.dat'
        gxypath = './tests/data/River_Sections_w_replicates.gxy'
        dat = DAT(datpath)
        gxy = GXY(gxypath)
        dat.add_gxy(gxy)
        unit = dat.unit('REPLICATE__DS_1b')
        output = unit.convert()
        self.assertEqual(1, 1)

    def test_interpolate_river(self):
        datpath = './tests/data/River_Sections_w_interpolates.dat'
        gxypath = './tests/data/River_Sections_w_interpolates.gxy'
        dat = DAT(datpath)
        gxy = GXY(gxypath)
        dat.add_gxy(gxy)
        unit = dat.unit('INTERPOLATE__DS_1a')
        output = unit.convert()
        self.assertEqual(1, 1)
