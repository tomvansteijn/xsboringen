# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.xmlfiles import borehole_from_xml

import numpy as np

import glob
import os

DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestBoreholeFromXML(object):
    def test_read(self):
        xmlfiles = glob.glob(os.path.join(DATADIR, '*1.4.xml'))
        boreholes = []
        for xmlfile in xmlfiles:
            boreholes.append(borehole_from_xml(xmlfile))
        assert len(boreholes) == 1700

    def test_read_segments(self):
        xmlfile = os.path.join(DATADIR, 'B39E0254_1.4.xml')
        b = borehole_from_xml(xmlfile)
        b.materialize()
        assert len(b) == 136
        assert np.isclose(b.segments[0].length, 2.)
        assert b.segments[-1].lithology == 'K'

    def test_read_simplify(self):
        xmlfile = os.path.join(DATADIR, 'B39E0254_1.4.xml')
        b = borehole_from_xml(xmlfile)
        b.simplify()
        assert len(b) == 82
        assert np.isclose(b.segments[0].length, 2.)
        assert b.segments[-1].lithology == 'K'
