# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsb.plot import plot_cross_section


class Cross_Section(object):
    def __init__(self, geometry, buffer_distance=None, label=None):
        self.geometry = geometry
        self.buffer_distance = buffer_distance
        self.label = label

    def add_boreholes(self, boreholes, buffer_distance=None):
        pass

    def add_piezometers(self, piezometers, buffer_distance=None):
        pass

    def add_points(self, points, buffer_distance=0.):
        pass

    def add_lines(self, lines):
        pass

    def add_solids(self, solids):
        pass

    def plot(self, imagefile):
        plot_cross_section(self, imagefile)
