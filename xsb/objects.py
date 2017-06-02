# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from collections import Iterable
from itertools import groupby


class AsDictMixin(object):
    '''Mixin for mapping class attributes to dictionary'''
    def as_dict(self, keys=None):
        if keys:
            return {k: getattr(self, k) for k in keys}
        else:
            return {k: v for k, v in self.__dict__.items()
                if not k.startswith('__')}


class Segment(AsDictMixin):
    '''Class representing borehole segment'''
    def __init__(self, top, base, lithology,
            sandmedianclass=None, fields=None):
        self.top = top
        self.base = base
        self.lithology = lithology
        self.sandmedianclass = sandmedianclass
        self.fields = fields

    def __repr__(self):
        return 'Segment(top={:.2f}, base={:.2f}, lithology={!s})'.format(
            self.top,
            self.base,
            self.lithology,
            )

    def __iadd__(self, other):
        self.top = min(self.top, other.top)
        self.base = max(self.base, other.base)
        return self

    @property
    def thickness(self):
        return self.base - self.top

    def relative_to(self, z):
        return z - self.top, z - self.base


class Borehole(AsDictMixin, Iterable):
    '''Borehole class with iterator method yielding segments'''
    def __init__(self, code, depth,
            fields=None, x=None, y=None, z=None,
            segments=None, verticals=None):
        self.code = code
        self.depth = depth
        self.fields = fields

        self.x = x
        self.y = y
        self.z = z

        self.segments = segments
        self.verticals = verticals

        self.materialized = False

    def __repr__(self):
        return 'Borehole(code={!s}, depth={:.2f})'.format(
            self.code,
            self.depth,
            )

    def __len__(self):
        if hasattr(self.segments, "__len__"):
            return len(self.segments)
        else:
            raise AttributeError('segments generator has no length')

    def __iter__(self):
        for segment in self.segments:
            yield segment

    @property
    def geometry(self):
        '''borehole geometry interface'''
        return {'type': 'Point', 'coordinates': (self.x, self.y)}

    def materialize(self):
        '''read borehole segments and assign as list'''
        segments_in_list = []
        for segment in self.segments:
            segments_in_list.append(segment)
        self.segments = segments_in_list
        self.materialized = True

    def simplify(self, min_thickness=0.):
        '''combine segments with same lithology and sandmedianclasses'''
        simple_segments = []
        key = lambda s: {
            'lithology': s.lithology,
            'sandmedianclass': s.sandmedianclass,
            }
        for i, (key, grouped) in enumerate(groupby(self.segments, key)):
            grouped_segments = [s for s in grouped]
            simplified = Segment(
                top=min(s.top for s in grouped_segments),
                base=max(s.base for s in grouped_segments),
                **key,
                )
            if (i == 0) or (simplified.thickness > min_thickness):
                simple_segments.append(simplified)
            else:
                simple_segments[-1] += simplified
        self.segments = simple_segments
        self.materialized = True


class CPT(Borehole):
    '''CPT class equal to borehole'''
    pass
