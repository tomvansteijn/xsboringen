# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import matplotlib.patheffects as PathEffects
from matplotlib import pyplot as plt
from matplotlib import transforms
import numpy as np

from collections import namedtuple
import logging
import os


class CrossSectionPlot(object):
    Extension = namedtuple('Extension', ['point', 'dx'])
    def __init__(self, cross_section, styles, config,
        xtickstep=None, ylim=None, xlabel=None, ylabel=None, legend_ncol=1,
        ):
        self.cs = cross_section
        self.styles = styles
        self.cfg = config

        self.xtickstep = xtickstep
        self.ylim = ylim
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend_ncol = legend_ncol

        self.point_distance = 'bycode'

    def __repr__(self):
        return ('{s.__class__.__name__:}(length={s.length:.2f}, '
                'styles={s.styles:}, '
                'label={s.label:})').format(s=self)

    @property
    def length(self):
        return self.cs.length

    @property
    def label(self):
        return self.cs.label

    def plot_borehole(self, ax, left, borehole, width):
        for segment in borehole:
            height = segment.thickness
            bottom = borehole.z - segment.base
            segment_style = self.styles['segments'].lookup(segment)

            # plot segment as bar
            rect = ax.bar(left, height, width, bottom,
                align='center', zorder=2,
                **segment_style)

        # plot borehole code as text
        codelabel_position = self.cfg.get('codelabel_position')
        codelabel_fontsize = self.cfg.get('codelabel_fontsize')
        codelabel_color = self.cfg.get('codelabel_color')
        vtrans = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
        txt = ax.text(left, codelabel_position, borehole.code,
            size=codelabel_fontsize,
            color=codelabel_color,
            rotation=90,
            ha='center', va='bottom',
            transform=vtrans,
            )

        return txt

    def plot_vertical(self, ax, distance, vertical, width, style):
        depth = np.array(vertical.depth, dtype=np.float)
        rescaled = np.array(vertical.rescaled().values, dtype=np.float)
        transformed = distance + (rescaled - 0.5)*width
        vert = ax.plot(transformed, depth, **style)
        return vert

    def plot_edge(self, ax, distance, vertical, width, style):
        height = vertical.depth[0] - vertical.depth[-1]
        bottom = vertical.depth[-1]
        # plot edge as bar
        rect = ax.bar(distance, height, width, bottom,
            align='center', zorder=2,
            **style)

    def plot_point(self, ax, point, extensions,
        plot_distance_by_code=None,
        borehole_z_by_code=None,
        ):
        plot_distance_by_code = plot_distance_by_code or {}
        borehole_z_by_code = borehole_z_by_code or {}
        if self.point_distance == 'bycode':
            plot_distance = plot_distance_by_code.get(point.code)   
            if plot_distance is None:
                return None
            if point.z is None:
                point.z = borehole_z_by_code.get(point.code)
        else:
            plot_distance = distance
            for extension in extensions:
                if distance >= extension.point:
                    plot_distance += extension.dx
        style = self.cfg['pointlabel_style']
        elements = []
        for value in point.values:
            if value.value is None:
                continue
            element = '{name:}: {value:}'.format(
                name=value.name,
                value=value.format.format(value.value),
                )
            elements.append(element)
        if len(elements) > 0:
            label = '\n'.join(elements)
            path_effects = [
                PathEffects.withStroke(linewidth=2, foreground='white'),
                ]
            txt = ax.text(plot_distance, point.midlevel, label,
                path_effects=path_effects,
                **style)
            return txt
        else:
            return None

    def plot_surface(self, ax, surface, extensions):
        distance, coords = zip(*self.cs.discretize(surface.res))
        distance = np.array(distance)
        plot_distance = distance.copy()
        for extension in extensions:
            plot_distance[distance > extension.point] += extension.dx
        values = [v for v in surface.sample(coords)]
        style = self.styles['surfaces'].lookup(surface.stylekey)
        sf = ax.plot(plot_distance, values, **style)

    def plot_solid(self, ax, solid, extensions, min_thickness=0.):
        distance, coords = zip(*self.cs.discretize(solid.res))
        distance = np.array(distance)
        plot_distance = distance.copy()
        for extension in extensions:
            plot_distance[distance > extension.point] += extension.dx
        top, base = zip(*((t, b) for t, b in solid.sample(coords)))
        top = np.array(top)
        base = np.array(base)
        style = self.styles['solids'].lookup(solid.stylekey)
        sld = ax.fill_between(plot_distance, base, top,
            where=(top - base) > min_thickness,
            **style,
            )

    def plot_label(self, ax):
        lt = ax.text(0, 1.01, self.label, weight='bold', size='large',
             transform=ax.transAxes)
        rt = ax.text(1, 1.01, self.label + '`', weight='bold', size='large',
             transform=ax.transAxes)
        return lt, rt

    @classmethod
    def get_extensions(cls, distance, min_distance):
        '''x-axis extensions'''
        extensions = []
        spacing = np.diff(distance)
        too_close = spacing < min_distance
        leftpoints = distance[1:][too_close]
        dxs = min_distance - spacing[too_close]
        for leftpoint, dx in zip(leftpoints, dxs):
            extensions.append(
                cls.Extension(
                    point=leftpoint,
                    dx=dx,
                    )
                )
        plot_distance = np.cumsum(
            np.concatenate([distance[:1], np.maximum(spacing, min_distance)])
            )
        return plot_distance, extensions

    def get_legend(self, ax):
        handles_labels = []
        if len(self.cs.boreholes) > 0:
            for label, style in self.styles['verticals'].items():
                handles_labels.append((
                    plt.Line2D([0, 1], [0, 1],
                        **style,
                        ),
                    label
                    ))
        for label, style in self.styles['surfaces'].items():
            handles_labels.append((
                plt.Line2D([0, 1], [0, 1],
                    **style,
                    ),
                label
                ))
        if len(self.cs.boreholes) > 0:
            for label, style in self.styles['segments'].items():
                handles_labels.append((
                    plt.Rectangle((0, 0), 1, 1,
                        **style,
                        ),
                    label
                    ))
        for label, style in self.styles['solids'].items():
            handles_labels.append((
                plt.Rectangle((0, 0), 1, 1,
                    **style,
                    ),
                label
                ))
        handles, labels = zip(*handles_labels)

        legend_title = self.cfg.get('legend_title')
        legend_fontsize = self.cfg.get('legend_fontsize')
        lgd = ax.legend(handles, labels,
            title=legend_title,
            fontsize=legend_fontsize,
            loc='lower left',
            bbox_to_anchor=(1.01, 0),
            ncol=self.legend_ncol,
            )
        return lgd

    def plot(self, ax):
        # bounding box extra artists (title, legend, labels, etc.)
        bxa = []

        # sort cross-section data by distance
        self.cs.sort()

        # calculate min distance
        min_distance_factor = self.cfg.get('min_distance_factor', 2.e-2)
        min_distance = min_distance_factor * self.length

        # boreholes
        boreholes = [b for d, b in self.cs.boreholes]

        # borehole distance vector
        distance = np.array([d for d, b in self.cs.boreholes])

        # x-axis limits
        xmin, xmax = [0., self.length]

        # adjust limits for first and last borehole
        if len(distance) > 0:
            min_limit_factor = self.cfg.get('min_limit_factor', 4.e-2)
            min_limit = min_limit_factor * self.length
            if distance[0] < (min_limit):
                xmin -= ((min_limit) - distance[0])
            if (xmax - distance[-1]) < (min_limit):
                xmax += ((min_limit) - (xmax - distance[-1]))

        # get plot_distance and x-axis extensions
        plot_distances, extensions = self.get_extensions(distance, min_distance)
        boreholes_plot_distances = zip(boreholes, plot_distances)

        # apply extensions to x-axis limits
        for extension in extensions:
            xmax += extension.dx

        # bar & vertical width
        barwidth_factor = self.cfg.get('barwidth_factor', 1.e-2)
        verticalwidth_factor = self.cfg.get('verticalwidth_factor', 1.e-2)
        barwidth = barwidth_factor * (xmax - xmin)
        verticalwidth = verticalwidth_factor * (xmax - xmin)

        # plot boreholes
        for borehole, plot_distance in boreholes_plot_distances:

            # plot borehole
            txt = self.plot_borehole(ax, plot_distance, borehole, barwidth)
            bxa.append(txt)

            # plot verticals
            for key in self.styles['verticals'].records:
                if key not in borehole.verticals:
                    continue
                vertical = borehole.verticals[key].relative_to(borehole.z)
                if vertical.isempty():
                    continue
                style = self.styles['verticals'].lookup(key)
                self.plot_vertical(
                    ax,
                    distance=plot_distance,
                    vertical=vertical,
                    width=verticalwidth,
                    style=style,
                    )

            if (len(borehole.segments) == 0) and (len(borehole.verticals) > 0):
                key = next(iter(self.styles['verticals'].records.keys()))
                vertical = borehole.verticals[key].relative_to(borehole.z)
                self.plot_edge(
                    ax,
                    distance=plot_distance,
                    vertical=vertical,
                    width=verticalwidth,
                    style=self.cfg.get('verticaledge_style') or {},
                    )

        # plot points
        plot_distance_by_code = {
            b.code: d for b, d in zip(boreholes, plot_distances)
            }
        borehole_z_by_code = {
            b.code: b.z for b in boreholes
            }
        for distance, point in self.cs.points:
            if point.midlevel is None:
                continue
            self.plot_point(ax,
                point=point,
                extensions=extensions,
                plot_distance_by_code=plot_distance_by_code,
                borehole_z_by_code=borehole_z_by_code,
                )

        # plot surfaces
        for surface in self.cs.surfaces:
            self.plot_surface(ax,
                surface=surface,
                extensions=extensions,
                )

        # plot solids
        for solid in self.cs.solids:
            self.plot_solid(ax,
                solid=solid,
                extensions=extensions,
                )

        # plot labels
        if self.label is not None:
            lt, rt = self.plot_label(ax)
            bxa.append(lt)
            bxa.append(rt)

        # axis ticks
        if self.xtickstep is not None:
            xticks = np.arange(0., self.length + self.xtickstep, self.xtickstep)
        else:
            xticks = ax.get_xticks().copy()

        fmt = self.cfg.get('xticklabel_format', '{:3.0f}')
        xticklabels = [fmt.format(x) for x in xticks]
        extended_xticks = xticks.copy()
        for extension in extensions:
            extended_xticks[xticks > extension.point] += extension.dx
        ax.set_xticks(extended_xticks)
        ax.set_xticklabels(xticklabels)

        # axis limits
        ax.set_xlim([xmin, xmax])
        if self.ylim is not None:
            ax.set_ylim(self.ylim)
        else:
            ax.autoscale(axis='y')

        # grid lines |--|--|--|
        ax.grid(linestyle='--', linewidth=0.5, color='black', zorder=0)

        # axis labels
        if self.xlabel is not None:
            ax.set_xlabel(self.xlabel)

        if self.ylabel is not None:
            ax.set_ylabel(self.ylabel)

        # legend
        lgd = self.get_legend(ax)
        if lgd is not None:
            bxa.append(lgd)

        # return list of extra artists
        return bxa

    def to_image(self, imagefile, **save_kwargs):
        # figure
        figsize = self.cfg.get('figure_size')
        fig, ax = plt.subplots(figsize=figsize)

        # plot cross-section
        bxa = self.plot(ax)

        # save figure
        plt.savefig(imagefile,
            bbox_inches='tight',
            bbox_extra_artists=bxa,
            dpi=self.cfg.get('figure_dpi', 200),
            **save_kwargs,
            )

        # clos figure
        plt.close()


def MapPlot(object):
    pass
