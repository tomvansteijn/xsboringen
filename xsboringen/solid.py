#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.rasterfiles import sample


class Solid(object):
    def __init__(self, name, topfile, basefile, res, stylekey=None):
        self.name = name

        self.topfile = topfile
        self.basefile = basefile
        self.res = res
        self.stylekey = stylekey

    def __repr__(self):
        return ('{s.__class__.__name__:}(name={s.name:}, '
            'res={s.res:.2f})').format(s=self)

    def sample(self, coords):
        sample_top_base = zip(
            sample(self.topfile, coords),
            sample(self.basefile, coords),
            )
        for top, base in sample_top_base:
            yield top, base
