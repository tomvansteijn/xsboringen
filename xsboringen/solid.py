#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.rasterfiles import sample_linestring

from shapely.geometry import shape


def get_solid_data(solid, linestring):
    linestring = shape(linestring)
    solid.data = solid.sample(linestring)
    return solid


class Solid(object):
    def __init__(self, name, topfile, basefile, data=None, stylekey=None):
        self.name = name

        self.topfile = topfile
        self.basefile = basefile
        self.data = data
        self.stylekey = stylekey

    def __repr__(self):
        return ('{s.__class__.__name__:}(name={s.name:})').format(s=self)

    @property
    def has_data(self):
        return self.data is not None

    def sample(self, linestring):
        dist, top = sample_linestring(self.topfile, linestring)
        dist, base = sample_linestring(self.basefile, linestring)
        return dist, top, base

    def sample_top(self, linestring):
        return sample_linestring(self.topfile, linestring)
    
    def sample_base(self, linestring):
        return sample_linestring(self.basefile, linestring)

