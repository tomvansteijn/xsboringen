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
class Well(AsDictMixin, CopyMixin):
    '''Well class'''
    Value = namedtuple('Value', ['name', 'value', 'dtype', 'format'])

    def __init__(self, code,
            x=None, y=None, z=None,
            filtertoplevel=None, filterbottomlevel=None,
            ):
        self.code = code

        self.x = x
        self.y = y
        self.z = z

        self.filtertoplevel = filtertoplevel
        self.filterbottomlevel = filterbottomlevel

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
        if (self.filtertoplevel is None) and (self.filterbottomlevel is None):
            return None
        elif self.filtertoplevel is None:
            return self.filterbottomlevel
        elif self.filterbottomlevel is None:
            return self.filtertoplevel
        else:
            return (self.filtertoplevel + self.filterbottomlevel) / 2.

    @property
    def depth(self):
        return self.z - self.filtertoplevel
    
    @property
    def filterlength(self):
        return self.filterbottomlevel - self.filtertoplevel

    def relative_to(self, z):
        '''return filtertoplevel and filterbottomlevel relative to z'''
        clone = self.copy()
        clone.filtertoplevel = z - self.filtertoplevel
        clone.filterbottomlevel = z - self.filterbottomlevel
        return clone

