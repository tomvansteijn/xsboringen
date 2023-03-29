# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from shapely.geometry import asShape, Point


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
        self.wells = []
        self.surfaces = []
        self.solids = []

    def __repr__(self):
        return ('{s.__class__.__name__:}(length={s.shape.length:.2f}, '
                'buffer_distance={s.buffer_distance:.2f}, '
                'label={s.label:})').format(s=self)

    @property
    def shape(self):
        return asShape(self.geometry)

    def add_boreholes(self, boreholes, selector=None):
        '''add boreholes within buffer distance and project to line'''
        self._add_some_objects(boreholes, self.boreholes, selector)

    def add_points(self, points, selector=None):
        '''add points within buffer distance and project to line'''
        self._add_some_objects(points, self.points, selector)

    def add_wells(self, wells, selector=None):
        '''add wells within buffer distance and project to line'''
        self._add_some_objects(wells, self.wells, selector)

    def _add_some_objects(self, some_objects, dst, selector=None):
        for an_object in some_objects:
            if (selector is not None) and (not selector(an_object)):
                continue
            if asShape(an_object.geometry).within(self.buffer):
                the_distance = self.shape.project(asShape(an_object.geometry))

                # explanation: the buffer extends beyond the endpoints of the cross-section
                # points beyond the endpoints but within the buffer are
                # projected at 0. and length distance with a sharp angle
                # these points are not added to the cross-section
                # points exactly at 0. or length distance are also not added
                if (the_distance > 0.) and (the_distance < self.shape.length):
                    dst.append((the_distance, an_object))

    def sort(self):
        self.boreholes = [b for b in sorted(self.boreholes)]
        self.wells = [w for w in sorted(self.wells)]
        self.points = [p for p in sorted(self.points)]

    @staticmethod
    def filter_unique_distance(objects):
        filtered = []
        unique_distances = set()
        for distance, object in objects:
            if distance not in unique_distances:
                filtered.append((distance, object))
            unique_distances.add(distance)
        return filtered

    def drop_duplicates(self):
        self.boreholes = self.filter_unique_distance(self.boreholes)
        self.wells = self.filter_unique_distance(self.wells)
        self.points = self.filter_unique_distance(self.points)

    def add_surface(self, surface):
        self.surfaces.append(surface)

    def add_solid(self, solid):
        self.solids.append(solid)
