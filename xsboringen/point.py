#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV


from xsboringen.mixins import AsDictMixin, CopyMixin

from collections import namedtuple
from functools import total_ordering

# ValuePoint
# labelpoint
# ClassifiedPoint
@total_ordering
class Point(AsDictMixin, CopyMixin):
    '''Point class'''
    Value = namedtuple('Value', ['name', 'value', 'dtype', 'format'])

    def __init__(self, code,
            x=None, y=None, z=None,
            top=None, base=None,
            values=None,
            ):
        self.code = code

        self.x = x
        self.y = y
        self.z = z

        self.top = top
        self.base = base

        self.values = [self.Value(**v) for v in values or []]

    def __repr__(self):
        return ('{s.__class__.__name__:}(code={s.code:})').format(
            s=self,
            )

    def __eq__(self, other):
        return self.midlevel == other.midlevel

    def __lt__(self, other):
        return self.midlevel < other.midlevel

    @property
    def geometry(self):
        '''borehole geometry interface'''
        return {'type': 'Point', 'coordinates': (self.x, self.y)}

    @property
    def midlevel(self):
        if (self.top is None) and (self.base is None):
            return None
        elif self.top is None:
            return self.base
        elif self.base is None:
            return self.top
        else:
            return (self.top + self.base) / 2.

    def relative_to(self, z):
        '''return top and base relative to z'''
        clone = self.copy()
        clone.top = z - self.top
        clone.base = z - self.base
        return clone

