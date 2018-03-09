#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.rasterfiles import sample


class Surface(object):
    def __init__(self, name, surfacefile, res, stylekey=None):
        self.name = name

        self.file = surfacefile
        self.res = res
        self.stylekey = stylekey

    def __repr__(self):
        return ('{s.__class__.__name__:}(name={s.name:}, '
            'res={s.res:.2f})').format(s=self)

    def sample(self, coords):
        for value in sample(self.file, coords):
            yield value
