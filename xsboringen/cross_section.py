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
        return ('{s.__class__.__name__:}(length={s.length:.2f}, '
                'buffer_distance={s.buffer_distance:.2f}, '
                'label={s.label:})').format(s=self)

    @property
    def shape(self):
        return asShape(self.geometry)

    @property
    def length(self):
        return self.shape.length

    def add_boreholes(self, boreholes):
        '''add boreholes within buffer distance and project to line'''
        self._add_some_objects(boreholes, self.boreholes)

    def add_points(self, points):
        '''add points within buffer distance and project to line'''
        self._add_some_objects(points, self.points)

    def add_wells(self, wells):
        '''add wells within buffer distance and project to line'''
        self._add_some_objects(wells, self.wells)

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
        self.wells = [w for w in sorted(self.wells)]
        self.points = [p for p in sorted(self.points)]        

    def add_surface(self, surface):
        self.surfaces.append(surface)

    def add_solid(self, solid):
        self.solids.append(solid)
