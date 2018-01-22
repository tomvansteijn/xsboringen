# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.geffiles import borehole_from_gef, GefFieldNames

import numpy as np

import glob
import os

DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

class TestBoreholeFromGEF(object):
    def test_read(self):
        geffile = os.path.join(DATADIR, 'DD286.+027_SB_BIK.GEF')
        repeatedset = {
            'columninfo',
            'columnvoid',
            'measurementtext',
            'measurementvar',
            'specimentext',
            'specimenvar',
        }
        fieldnames = GefFieldNames(**{
            'columnsep': 'columnseparator',
            'code': 'testid',
            'depth': 'einddiepte',
            'xy': 'xyid',
            'z': 'zid',
            })
        borehole = borehole_from_gef(geffile, fieldnames, repeatedset)
        assert np.isclose(borehole.z, 14.21)
        borehole.materialize()
