#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

# from xsboringen.rasterfiles import sample


class Surface(object):
    def __init__(self, name, surfacefile, res, stylekey=None):
        self.name = name

        self.file = surfacefile
        self.stylekey = stylekey

    def __repr__(self):
        return ('{s.__class__.__name__:}(name={s.name:})').format(s=self)

    def sample(self, linestring):
        return sample_linestring(self.file, linestring)
