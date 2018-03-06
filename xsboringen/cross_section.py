# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.rasterfiles import sample

from shapely.geometry import asShape, Point


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


class CrossSection(object):
    def __init__(self, geometry, buffer_distance, label=''):
        self.geometry = geometry
        self.buffer_distance = buffer_distance
        self.label = label

        # geometric buffer with given distance
        self.buffer = self.shape.buffer(buffer_distance)

        # initialize data atttributes to empty lists
        self.boreholes = []
        self.points = []
        self.surfaces = []
        self.solids = []

    def __repr__(self):
        return ('{s.__class__.__name__:}(length={s.length:.2f}, '
                'buffer_distance={s.buffer_distance:.2f}, '
                'label={s.label:})').format(s=self)

    @property
    def shape(self):
        return asShape(self.geometry)

    @property
    def length(self):
        return self.shape.length

    def discretize(self, res):
        '''discretize line to point coords with given distance'''
        d = 0.
        while d <= self.shape.length:
            p = self.shape.interpolate(d)
            yield d, (p.x, p.y)
            d += res

    def add_boreholes(self, boreholes):
        '''add boreholes within buffer distance and project to line'''
        self._add_some_objects(boreholes, self.boreholes)

    def add_points(self, points):
        '''add points within buffer distance and project to line'''
        self._add_some_objects(points, self.points)

    def _add_some_objects(self, some_objects, dst):
        for an_object in some_objects:
            if asShape(an_object.geometry).within(self.buffer):
                the_distance = self.shape.project(asShape(an_object.geometry))

                # explanation: the buffer extends beyond the endpoints of the cross-section
                # points beyond the endpoints but within the buffer are
                # projected at 0. and length distance with a sharp angle
                # these points are not added to the cross-section
                # points exactly at 0. or length distance are also not added
                if (the_distance > 0.) and (the_distance < self.length):
                    dst.append((the_distance, an_object))

    def sort(self):
        self.boreholes = [b for b in sorted(self.boreholes)]
        self.points = [p for p in sorted(self.points)]

    def add_surfaces(self, surfaces):
        for surface in surfaces:
            distance, coords = zip(*self.discretize(surface['res']))
            self.surfaces.append(surface(
                name=Surface['name'],
                distance=[d for d in distance],
                values=[v for v in sample(surface['file'], coords)],
                ))

    def add_solids(self, solids):
        for solid in solids:
            distance, coords = zip(*self.discretize(solid['res']))
            self.solids.append(Solid(
                name=solid['name'],
                distance=[d for d in distance],
                top=[t for t in sample(solid['topfile'], coords)],
                base=[b for b in sample(solid['basefile'], coords)],
                ))

