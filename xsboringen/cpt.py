# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.borehole import Borehole, Segment

from collections import namedtuple


class CPT(Borehole):
    '''CPT class inherits from borehole'''
    _keys = 'cone_resistance', 'friction_ratio'
    Row = namedtuple('Row', ('depth',) + _keys)

    @property
    def complete(self):
        return all (k in self.verticals for k in self._keys)

    @property
    def rows(self):
        zipped = zip(
            self.verticals['cone_resistance'],
            self.verticals['friction_ratio'],
            )
        for (depth, qc), (depth, rf) in zipped:
            if depth is not None:
                yield self.Row(depth, qc, rf)

    def classify_lithology(self, classifier, admixclassifier=None):
        if self.complete:
            self.segments = []
            for i, row in enumerate(self.rows):
                base = row.depth
                if i == 0:
                    top = 0.
                    blind_segment = Segment(top, base, "O")
                    self.segments.append(blind_segment)
                    top = base
                    continue
                lithology = classifier.classify(
                    row.friction_ratio,
                    row.cone_resistance,
                    )
                segment = Segment(top, base, lithology)
                segment.update(admixclassifier.classify(segment.lithology))
                self.segments.append(segment)
                top = base

    def to_lithology(self, classifier, admixclassifier):
        self.classify_lithology(classifier, admixclassifier)
        return self



