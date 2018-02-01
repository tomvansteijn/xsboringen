# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.geffiles import GefCPTFile, GefBoreholeFile

import numpy as np

import glob
import os

DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestBoreholeFromGEF(object):
    def test_read(self):
        geffile = os.path.join(DATADIR, 'DD286.+027_SB_BIK.GEF')
        fieldnames = {
            'columnsep': 'COLUMNSEPARATOR',
            'recordsep': 'RECORDSEPARATOR',
            'code': 'TESTID',
            'xy': 'XYID',
            'z': 'ZID',
            }
        gef = GefBoreholeFile(geffile, fieldnames)
        borehole = gef.to_borehole()
        assert np.isclose(borehole.z, 14.21)
        borehole.materialize()
        assert borehole.segments[-2].lithology == 'Zs1g1'
        assert borehole.segments[-2].color == ['GR',]


class TestCPTFromGEF(object):
    def test_read(self):
        geffile = os.path.join(DATADIR, '594781_TG322.+039_SW_KR.GEF')
        fieldnames = {
            'columnsep': 'COLUMNSEPARATOR',
            'recordsep': 'RECORDSEPARATOR',
            'code': 'TESTID',
            'xy': 'XYID',
            'z': 'ZID',
            }
        columns = GefColumns(**{
            'depth': '',
            'cone_resistance': '',
            'friction_ratio': '',
            })

        cpt = gef.to_cpt(geffile, fieldnames, columns)

