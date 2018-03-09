#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV


class Surface(object):
    def __init__(self, name, distance, values):
        self.name = name

        assert len(distance) == len(values), \
            'distance and values should have equal length'

        self.distance = distance
        self.values = values

    def __repr__(self):
        return ('{s.__class__.__name__:}(length={s.length:.2f}, '
                'name={s.name:})').format(s=self)

    def __iter__(self):
        for d, v in zip(self.distance, self.values):
            yield d, v

    @property
    def length(self):
        return max(self.distance) - min(self.distance)
