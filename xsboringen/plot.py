# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from matplotlib import pyplot as plt
from matplotlib import transforms
import numpy as np

from collections import namedtuple
import logging
import os


class CrossSectionPlot(object):
    Extension = namedtuple('Extension', ['point', 'dx'])
    def __init__(self, cross_section, styles, config,
        xtickstep=None, ylim=None, xlabel=None, ylabel=None,
        ):
        self.cs = cross_section
        self.styles = styles
        self.cfg = config

        self.xtickstep = xtickstep
        self.ylim = ylim
        self.xlabel = xlabel
        self.ylabel = ylabel

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
        vtrans = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
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
        txt = ax.text(left, codelabel_position, borehole.code,
            size=codelabel_fontsize,
            color=codelabel_color,
            rotation=90,
            ha='center', va='bottom',
            transform=vtrans,
            )

        return txt

    def plot_vertical(self, ax, distance, vertical):
        style = self.styles['verticals'].lookup(vertical.name)
        vrt = ax.plot(ax, vertical.values, vertical.depth,
            **style,
            )

    def plot_point(self, ax, distance, point):
        for field, value in point.items():
            style = self.styles['points'].lookup(point.name)
            pnt = ax.plot(distance, value, **style[field])

    def plot_line(self, ax, line):
        style = self.styles['lines'].lookup(line.name)
        ln = ax.plot(line.distance, line.values, **style)

    def plot_solid(self, ax, solid):
        style = self.styles['solids'].lookup(solid.name)
        sld = ax.fill_between(solid.distance, solid.base, solid.top, **style)

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
        points = distance[1:][too_close]
        dxs = np.maximum(spacing[too_close], min_distance) - spacing[too_close]
        for point, dx in zip(points, dxs):
            extensions.append(
                cls.Extension(
                    point=point,
                    dx=dx,
                    )
                )
        return extensions

    def get_legend(self, ax):
        handles_labels = []
        for label, style in self.styles['segments'].items():
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
            bbox_to_anchor=(1, 0),
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

        # borehole distance vector
        distance = np.array([d for d, b in self.cs.boreholes])

        # x-axis limits
        xmin, xmax = [0., self.length]

        # adjust limits for first and last borehole
        min_limit_factor = self.cfg.get('min_limit_factor', 4.e-2)
        min_limit = min_limit_factor * self.length
        if distance[0] < (min_limit):
            xmin -= ((min_limit) - distance[0])
        if (xmax - distance[-1]) < (min_limit):
            xmax += ((min_limit) - (xmax - distance[-1]))

        # get x-axis extensions
        extensions = self.get_extensions(distance, min_distance)

        # apply extensions to x-axis limits
        for extension in extensions:
            xmax += extension.dx

        # bar & vertical width
        barwidth_factor = self.cfg.get('barwidth_factor', 1.e-2)
        verticalwidth_factor = self.cfg.get('verticalwidth_factor', 2.e-2)
        barwidth = barwidth_factor * (xmax - xmin)
        verticalwidth = verticalwidth_factor * (xmax - xmin)

        # plot boreholes
        for distance, borehole in self.cs.boreholes:
            # apply extensions
            plot_distance = distance
            for extension in extensions:
                if (
                    np.isclose(distance, extension.point) or
                    (distance > extension.point)
                    ):
                    plot_distance += extension.dx

            # plot borehole
            txt = self.plot_borehole(ax, plot_distance, borehole, barwidth)
            bxa.append(txt)

            # plot verticals
            if borehole.verticals is not None:
                for vertical in borehole.verticals:
                    self.plot_vertical(ax,
                        plot_distance, vertical)

        # plot points
        for distance, point in self.cs.points:
            self.plot_point(ax,
                distance, point,
                )

        # plot lines
        for line in self.cs.lines:
            self.plot_line(ax,
                line, **self.style['lines'].lookup(line)
                )

        # plot solids
        for solid in self.cs.solids:
            self.plot_solid(ax,
                solid,
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
        for extension in extensions:
            xticks[xticks > extension.point] += extension.dx
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)

        # axis limits
        ax.set_xlim([xmin, xmax])
        if self.ylim is not None:
            ax.set_ylim(self.ylim)

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
            **save_kwargs,
            )

        # clos figure
        plt.close()
