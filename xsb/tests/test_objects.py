# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsb.objects import Borehole, Segment, CPT

import numpy as np

class TestSegment(object):
    def test_segment_lithology(self):
        s = Segment(top=0., base=10., lithology='Z')
        assert s.lithology == 'Z'

    def test_segment_thickness(self):
        s = Segment(top=0., base=10., lithology='Z')
        assert np.isclose(s.base, 10.)

    def test_segment_add_top(self):
        s1 = Segment(top=0., base=10., lithology='Z')
        s2  = Segment(top=10., base=12., lithology='K')
        s1 += s2
        assert np.isclose(s1.top, 0.)

    def test_segment_add_base(self):
        s1 = Segment(top=0., base=10., lithology='Z')
        s2  = Segment(top=10., base=12., lithology='K')
        s1 += s2
        assert np.isclose(s1.base, 12.)

    def test_segment_add_lithology(self):
        s1 = Segment(top=0., base=10., lithology='Z')
        s2  = Segment(top=10., base=12., lithology='K')
        s1 += s2
        assert s1.lithology == 'Z'

    def test_segment_relative_to(self):
        z = 13.
        s = Segment(top=5., base=7., lithology='Z')
        ref_top, ref_base = s.relative_to(z)
        assert np.isclose(ref_top, 8.)
        assert np.isclose(ref_base, 6.)


class TestBorehole(object):
    def test_borehole_depth(self):
        b = Borehole(code='b', depth=1.2)
        assert np.isclose(b.depth, 1.2)

    def test_borehole_iter(self):
        s_iter = (s for s in [
            Segment(top=0., base=0.5, lithology='Z'),
            Segment(top=0.5, base=3.0, lithology='K'),
            Segment(top=3.0, base=20., lithology='Z'),
            ])
        b = Borehole(code='b', depth=20., segments=s_iter)
        b.materialize()
        assert len(b) == 3

    def test_simplify(self):
        segments = [
            Segment(top=0., base=0.5, lithology='Z'),
            Segment(top=0.5, base=3.0, lithology='Z'),
            Segment(top=3.0, base=10.0, lithology='K'),
            Segment(top=10.0, base=20., lithology='Z'),
            ]
        b = Borehole(code='b', depth=20., segments=segments)
        b.simplify()
        assert len(b) == 3
        assert b.segments[0].lithology == 'Z'
        assert np.isclose(b.segments[0].thickness, 3.0)

    def test_simplify_min_thickness(self):
        segments = [
            Segment(top=0., base=0.5, lithology='Z'),
            Segment(top=0.5, base=3.0, lithology='Z'),
            Segment(top=3.0, base=3.1, lithology='K'),
            Segment(top=10.0, base=20., lithology='Z'),
            ]
        b = Borehole(code='b', depth=20., segments=segments)
        b.simplify(min_thickness=0.5)
        assert len(b) == 2
        assert b.segments[0].lithology == 'Z'
        assert np.isclose(b.segments[0].thickness, 3.1)
