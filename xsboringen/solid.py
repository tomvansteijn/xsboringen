#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.rasterfiles import sample_linestring


class Solid(object):
    def __init__(self, name, topfile, basefile, res, stylekey=None):
        self.name = name

        self.topfile = topfile
        self.basefile = basefile
        self.stylekey = stylekey

    def __repr__(self):
        return ('{s.__class__.__name__:}(name={s.name:})').format(s=self)

    def sample(self, linestring):
        dist, top = sample_linestring(self.topfile, linestring)
        dist, base = sample_linestring(self.basefile, linestring)
        return dist, top, base

    def sample_top(self, linestring):
        return sample_linestring(self.topfile, linestring)
    
    def sample_base(self, linestring):
        return sample_linestring(self.basefile, linestring)

