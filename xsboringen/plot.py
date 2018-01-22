# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from matplotlib import pyplot as plt
from matplotlib import transforms

import logging
import os


class CrossSectionPlot(object):
    def __init__(self, cross_section, styles, config,
        ylim=None, xlabel=None, ylabel=None,
        ):
        self.cs = cross_section
        self.styles = styles
        self.cfg = config

        self.ylim = ylim
        self.xlabel = xlabel
        self.ylabel = ylabel


    def __repr__(self):
        return ('{s.__class__.__name__:}(length={s.length:.2f}, '
                'styles={s.styles:}, '
                'label={s.label:})').format(s=self)

    @property
    def label(self):
        return self.cs.label

    @property
    def length(self):
        return self.cs.length

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
            codelabel_position = self.cfg.get('codelabel.position')
            codelabel_fontsize = self.cfg.get('codelabel.fontsize')
            codelabel_color = self.cfg.get('codelabel.color')
            txt = ax.text(left, codelabel_position, borehole.code,
                size=codelabel_fontsize,
                color=codelabel_color,
                rotation=90,
                ha='center', va='bottom',
                transform=vtrans,
                )

            yield txt

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

    def get_width(self, factor):
        '''bar width from cross-section length'''
        width = self.cs.length * factor
        return width

    def get_xlim(self):
        return [0., self.cs.length]

    def get_legend(self, ax):
        handles_labels = []
        for label, style in self.styles['segments'].items():
            handles_labels.append((
                plt.Rectangle((0, 0), 1, 1,
                    facecolor=style.pop('color'),
                    **style,
                    ),
                label
                ))
        handles, labels = zip(*handles_labels)

        legend_title = self.cfg.get('legend.title')
        legend_fontsize = self.cfg.get('legend.fontsize')
        lgd = ax.legend(handles, labels,
            title=legend_title,
            fontsize=legend_fontsize,
            loc='lower left',
            bbox_to_anchor=(1, 0),
            )
        return lgd

    def plot_map(self, ax):
        # bounding box extra artists (title, legend, labels, etc.)
        bxa = []

        # set aspect to equal
        ax.set_aspect('equal')

        # plot cross-section
        x, y = zip(*self.cs.geometry['coordinates'])
        ax.plot(x, y, linestyle='-', color='black')

        # labels
        lt = ax.text(x[0], y[0], self.label, weight='bold', size='large')
        rt = ax.text(x[-1], y[-1], self.label + '`', weight='bold', size='large')



        # grid lines |--|--|--|
        ax.grid(linestyle='--', color='gray', zorder=0)

        return bxa


    def plot(self, ax):
        # bounding box extra artists (title, legend, labels, etc.)
        bxa = []

        # plot boreholes
        barwidth_factor = self.cfg.get('barwidth.factor') or 1.e-2
        verticalwidth_factor = self.cfg.get('verticalwidth.factor') or 2.e-2
        barwidth = self.get_width(barwidth_factor)
        verticalwidth = self.get_width(verticalwidth_factor)
        for distance, borehole in self.cs.boreholes:
            for txt in self.plot_borehole(ax,
                    distance, borehole, barwidth,
                    ):
                bxa.append(txt)

            # plot verticals
            if borehole.verticals is not None:
                for vertical in borehole.verticals:
                    self.plot_vertical(ax,
                        distance, vertical)

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

        # axis limits
        ax.set_xlim(self.get_xlim())
        if self.ylim is not None:
            ax.set_ylim(self.ylim)

        # grid lines |--|--|--|
        ax.grid(linestyle='--', color='gray', zorder=0)

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

    def save(self, imagefile, **save_kwargs):
        # figure
        figsize = self.cfg.get('figure.size')
        fig, ax = plt.subplots(figsize=figsize)

        # plot cross-section
        bxa = self.plot(ax)

        # save figure
        plt.savefig(imagefile,
            bbox_inches='tight',
            bbox_extra_artists=bxa,
            **save_kwargs,
            )
