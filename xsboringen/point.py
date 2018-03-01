#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV


from xsboringen.mixins import AsDictMixin, CopyMixin

from functools import total_ordering


@total_ordering
class Point(AsDictMixin, CopyMixin):
    '''Point class'''

    def __init__(self, code,
            x=None, y=None, z=None,
            top=None, base=None,
            textfields=None,
            ):
        self.code = code

        self.x = x
        self.y = y
        self.z = z

        self.top = top
        self.base = base

        self.textfields = textfields or []

    def __repr__(self):
        return ('{s.__class__.__name__:}(code={s.code:})').format(
            s=self,
            )

    def __eq__(self, other):
        return self.z == other.z

    def __lt__(self, other):
        return self.z < other.z


