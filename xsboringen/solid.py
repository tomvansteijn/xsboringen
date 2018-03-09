#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV


class Solid(object):
    def __init__(self, name, distance, top, base):
        self.name = name

        assert len(distance) == len(top) == len(distance), \
            'distance, top and base should have equal length'

        assert np.all(np.array(top) >= np.array(base)), \
            'top should be above base'

        self.distance = distance
        self.top = top
        self.base = base

    def __repr__(self):
        return ('{s.__class__.__name__:}(length={s.length:.2f}, '
                'name={s.name:})').format(s=self)

    def __iter__(self):
        for d, t, b in zip(self.distance, self.top, self.base):
            yield d, t, b

    @property
    def length(self):
        return max(self.distance) - min(self.distance)
