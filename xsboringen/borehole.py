# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.mixins import AsDictMixin, CopyMixin

from collections.abc import Iterable
from itertools import groupby
from functools import total_ordering


class Segment(AsDictMixin, CopyMixin):
    '''Class representing borehole segment'''

    # class attributes
    fieldnames = 'top', 'base', 'lithology', 'sandmedianclass'

    def __init__(self, top, base, lithology,
            sandmedianclass=None, **attrs):
        self.top = top
        self.base = base
        self.lithology = lithology
        self.sandmedianclass = sandmedianclass

        # set other properties
        for key, value in attrs.items():
            setattr(self, key, value)

    def __repr__(self):
        return ('{s.__class__.__name__:}(top={s.top:.2f}, '
                'base={s.base:.2f}, '
                'lithology={s.lithology:}, '
                'sandmedianclass={s.sandmedianclass:})').format(s=self)

    def __add__(self, other):
        clone = self.copy()
        clone.add(other)
        return clone

    def __radd__(self, other):
        return self

    def __iadd__(self, other):
        self.add(other)
        return self

    def add(self, other):
        if self.rel_sl:
            self.top = min(self.top, other.top)
            self.base = max(self.base, other.base)
        else:
            self.top = max(self.top, other.top)
            self.base = min(self.base, other.base)

    @property
    def thickness(self):
        '''thickness of segment'''
        return abs(self.base - self.top)

    @property
    def rel_sl(self):
        '''relative to surface level'''
        return self.top < self.base

    def relative_to(self, z):
        '''return top and base relative to z'''
        clone = self.copy()
        clone.top = z - self.top
        clone.base = z - self.base
        return clone

    def update(self, attrs):
        for key, value in attrs.items():
            setattr(self, key, value)


class Vertical(AsDictMixin, CopyMixin):
    def __init__(self, name, depth, values):
        self.name = name
        self.depth = depth
        self.values = values

    def __repr__(self):
        return ('{s.__class__.__name__:}(name={s.name:}, '
            'count={s.count:})').format(s=self)

    def __len__(self):
        return len(self.depth)

    def __iter__(self):
        for depth, value in zip(self.depth, self.values):
            yield depth, value

    @property
    def count(self):
        return sum(v is not None for v in self.values)

    def isempty(self):
        return all(v is None for v in self.values)

    def relative_to(self, z):
        clone = self.copy()
        clone.depth = [z - d if (d is not None) else None for d in self.depth]
        return clone

    def rescaled(self):
        clone = self.copy()
        vmin = min(v for v in self.values if (v is not None) and (v > 0))
        vmax = max(v for v in self.values if (v is not None) and (v > 0))
        clone.values = [
            (v - vmin) / (vmax - vmin)
            if (v is not None) and (v > 0) else None
            for v in self.values
            ]
        return clone


@total_ordering
class Borehole(AsDictMixin, CopyMixin, Iterable):
    '''Borehole class with iterator method yielding segments'''

    # class attributes
    fieldnames = ('code', 'depth', 'x', 'y', 'z')
    schema = {
            'geometry': 'Point',
            'properties': [
                ('code', 'str'),
                ('depth', 'float'),
                ('x', 'float'),
                ('y', 'float'),
                ('z', 'float')]
                }

    def __init__(self, code, depth,
            x=None, y=None, z=None,
            segments=None, verticals=None, **attrs):
        self.code = code
        self.depth = depth

        self.x = x
        self.y = y
        self.z = z

        self.segments = segments or []
        self.verticals = verticals or {}

        # set other properties
        for key, value in attrs.items():
            setattr(self, key, value)

    def __repr__(self):
        return ('{s.__class__.__name__:}(code={s.code:}, '
                'depth={s.depth:.2f})').format(
            s=self,
            )

    def __len__(self):
        if hasattr(self.segments, "__len__"):
            return len(self.segments)
        else:
            raise AttributeError('segments generator has no length')

    def __iter__(self):
        for segment in self.segments:
            yield segment

    def __eq__(self, other):
        return self.depth == other.depth

    def __lt__(self, other):
        return self.depth < other.depth

    @property
    def geometry(self):
        '''borehole geometry interface'''
        return {'type': 'Point', 'coordinates': (self.x, self.y)}

    def isempty(self):
        return len(self.segments) == 0

    def simplified(self, min_thickness=None, by=None):
        '''simplify clone and return for generator chaining'''
        clone = self.copy()
        clone.simplify(min_thickness=min_thickness, by=by)
        return clone

    def groupby(self, by=None):
        '''group segments using groupby function'''
        for key, grouped in groupby(self.segments, by):
            yield key, grouped

    def simplify(self, min_thickness=None, by=None):
        '''combine segments according to grouped attributes'''
        simple_segments = []
        for key, segments in self.groupby(by=by):
            simple_segments.append(sum(s for s in segments))
        self.segments = simple_segments

        if (min_thickness is not None) and not self.isempty():
            self.apply_min_thickness(min_thickness)
            self.simplify(min_thickness=None, by=by)

    def get_min_thickness(self):
        return min((s.thickness, i) for i, s in enumerate(self.segments))

    def apply_min_thickness(self, min_thickness):
        smallest_thickness, idx = self.get_min_thickness()
        while smallest_thickness < min_thickness:
            if idx > 0:
                segment_above = self.segments[idx - 1]
            else:
                segment_above = None
            try:
                segment_below = self.segments[idx + 1]
            except IndexError:
                segment_below = None
            if (segment_above is None) and (segment_below is None):
                break
            elif not smallest_thickness > 0.:
                del self.segments[idx]
            elif segment_above is None:
                self.segments[idx + 1].top = self.segments[idx].top
                del self.segments[idx]
            elif segment_below is None:
                self.segments[idx - 1].base = self.segments[idx].base
                del self.segments[idx]
            elif segment_above.thickness < segment_below.thickness:
                self.segments[idx - 1].base = self.segments[idx].base
                del self.segments[idx]
            else:
                self.segments[idx + 1].top = self.segments[idx].top
                del self.segments[idx]
            smallest_thickness, idx = self.get_min_thickness()

    def update_sandmedianclass(self, classifier):
        for segment in self.segments:
            if (
                (segment.sandmedianclass is None) and
                (getattr(segment, 'sandmedian', None) is not None)
                ):
                try:
                    sandmedian = float(segment.sandmedian)
                except ValueError:
                    continue
                segment.sandmedianclass = classifier.classify(sandmedian)
        return self

    def to_lithology(self, *args, **kwargs):
        return self
