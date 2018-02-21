# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from collections import Iterable
from itertools import groupby
from functools import total_ordering
import copy


class AsDictMixin(object):
    '''Mixin for mapping class attributes to dictionary'''
    def as_dict(self, keys=None):
        if keys:
            return {k: getattr(self, k, None) for k in keys}
        else:
            return {k: v for k, v in self.__dict__.items()
                if not k.startswith('__')}


class CopyMixin(object):
    '''Mixin for adding copy method to object'''
    def copy(self, deep=False):
        if deep:
            return copy.deepcopy(self)
        else:
            return copy.copy(self)


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
        clone.top = min(self.top, other.top)
        clone.base = max(self.base, other.base)
        return clone

    def __radd__(self, other):
        return self

    def __iadd__(self, other):
        self.top = min(self.top, other.top)
        self.base = max(self.base, other.base)
        return self

    @property
    def thickness(self):
        '''thickness of segment'''
        return self.base - self.top

    def relative_to(self, z):
        '''return top and base relative to z'''
        return z - self.top, z - self.base

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
            segments=None, verticals=None,
            **attrs,
            ):
        self.code = code
        self.depth = depth

        self.x = x
        self.y = y
        self.z = z

        self.segments = segments
        self.verticals = verticals

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
        if self.segments is not None:
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

    @property
    def materialized(self):
        '''segments materialized? (generator = False, list = True)'''
        return isinstance(self.segments, list)

    def materialize(self):
        '''read borehole segments and assign as list'''
        segments_in_list = []
        for segment in self.segments:
            segments_in_list.append(segment)
        self.segments = segments_in_list

    def simplified(self, min_thickness=None, by=None):
        '''simplify clone and return for generator chaining'''
        clone = self.copy()
        clone.simplify(min_thickness=min_thickness, by=by)
        return clone

    def groupby(self, by=None):
        '''group segments using groupby function or attribute(s)'''
        if self.segments is not None:
            if by is not None:
                if callable(by):
                    pass
                elif isinstance(by, str):
                    by = lambda s: {by: getattr(s, by)}
                else:
                    by = lambda s: {a: getattr(s, a) for a in by}
            else:
                by = lambda s: {
                    'lithology': s.lithology,
                    'sandmedianclass': s.sandmedianclass,
                    }

            for key, grouped in groupby(self.segments, by):
                yield key, grouped

    def simplify(self, min_thickness=None, by=None):
        '''combine segments according to grouped attributes'''
        if self.segments is not None:
            simple_segments = []
            for key, segments in self.groupby(by=by):
                simple_segments.append(sum(s for s in segments))
            self.segments = simple_segments

            if min_thickness is not None:
                self.apply_min_thickness(min_thickness)
                self.simplify(min_thickness=None)

    def _get_min_thickness(self):
        return min((s.thickness, i) for i, s in enumerate(self.segments))

    def apply_min_thickness(self, min_thickness):
        smallest_thickness, idx = self._get_min_thickness()
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
            smallest_thickness, idx = self._get_min_thickness()

    def update_sandmedianclass(self, classifier):
        if self.segments is not None:
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
