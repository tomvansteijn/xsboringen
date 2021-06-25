#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.rasterfiles import sample_linestring

from shapely.geometry import asShape


def get_surface_data(surface, linestring):
    linestring = asShape(linestring)
    surface.data = surface.sample(linestring)
    return surface


class Surface(object):
    def __init__(self, name, surfacefile, data=None, stylekey=None):
        self.name = name

        self.file = surfacefile
        self.data = data
        self.stylekey = stylekey

    def __repr__(self):
        return ('{s.__class__.__name__:}(name={s.name:})').format(s=self)

    @property
    def has_data(self):
        return self.data is not None

    def sample(self, linestring):
        return sample_linestring(self.file, linestring)
