# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.borehole import Borehole, Segment

from collections import namedtuple


class CPT(Borehole):
    '''CPT class inherits from borehole'''
    _keys = 'depth', 'cone_resistance', 'friction_ratio'
    Row = namedtuple('Row', _keys)

    @property
    def complete(self):
        return all (k in self.verticals for k in self._keys)

    @property
    def rows(self):
        if self.verticals is not None:
            zipped = zip(
                self.verticals['depth'],
                self.verticals['cone_resistance'],
                self.verticals['friction_ratio'],
                )
            for depth, qc, rf in zipped:
                if depth is not None:
                    yield self.Row(depth, qc, rf)

    def classify_lithology(self, classifier):
        if (self.verticals is not None) and self.complete:
            self.segments = []
            top = 0.
            for row in self.rows:
                base = row.depth
                lithology = classifier.classify(
                    row.friction_ratio,
                    row.cone_resistance,
                    )
                segment = Segment(top, base, lithology)
                self.segments.append(segment)
                top = base

    def to_lithology(self, classifier):
        self.classify_lithology(classifier)
        return self



