# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import matplotlib.patheffects as PathEffects
from matplotlib import pyplot as plt
from matplotlib import transforms
import numpy as np

from functools import partial
import logging
import os


class CrossSectionPlot(object):
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

    def plot_borehole(self, ax, distance, borehole, extensions, width):
        plot_distance = extensions(distance)
        for segment in borehole:
            height = segment.thickness
            bottom = borehole.z - segment.base
            segment_style = self.styles['segments'].lookup(segment)

            # plot segment as bar
            rect = ax.bar(plot_distance, height, width, bottom,
                align='center', zorder=2,
                **segment_style)

        # plot borehole code as text
        codelabel_position = self.cfg.get('codelabel_position')
        codelabel_fontsize = self.cfg.get('codelabel_fontsize')
        codelabel_color = self.cfg.get('codelabel_color')
        vtrans = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
        txt = ax.text(plot_distance, codelabel_position, borehole.code,
            size=codelabel_fontsize,
            color=codelabel_color,
            rotation=90,
            ha='center', va='bottom',
            transform=vtrans,
            )

        return txt

    def plot_vertical(self, ax, distance, vertical, extensions, width, style):
        plot_distance = extensions(distance)
        depth = np.array(vertical.depth, dtype=np.float)
        rescaled = np.array(vertical.rescaled().values, dtype=np.float)
        transformed = plot_distance + (rescaled - 0.5)*width
        vert = ax.plot(transformed, depth, **style)
        return vert

    def plot_edge(self, ax, distance, vertical, extensions, width, style):
        plot_distance = extensions(distance)
        height = vertical.depth[0] - vertical.depth[-1]
        bottom = vertical.depth[-1]
        # plot edge as bar
        rect = ax.bar(plot_distance, height, width, bottom,
            align='center', zorder=2,
            **style)

    def plot_well(self, ax, distance, well, extensions, width):
        plot_distance = extensions(distance)
        wellfilter = ax.bar(plot_distance, well.filterlength, width, well.z - well.filterbottomlevel,
                align='center', zorder=2,
                facecolor="dodgerblue", edgecolor="darkblue")
                
        standpipe = ax.bar(plot_distance, well.filtertoplevel, width, well.z - well.filtertoplevel,
                align='center', zorder=2,
                facecolor="none", edgecolor="darkblue")

        # plot well code as text
        codelabel_position = self.cfg.get('codelabel_position')
        codelabel_fontsize = self.cfg.get('codelabel_fontsize')
        codelabel_color = self.cfg.get('codelabel_color')
        vtrans = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
        txt = ax.text(plot_distance, codelabel_position, well.code,
            size=codelabel_fontsize,
            color=codelabel_color,
            rotation=90,
            ha='center', va='bottom',
            transform=vtrans,
            )

        return txt



    def plot_point(self, ax, distance, point, extensions,
        ):
        plot_distance = extensions(distance)
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
        plot_distance = extensions(distance)
        values = [v for v in surface.sample(coords)]
        style = self.styles['surfaces'].lookup(surface.stylekey)
        sf = ax.plot(plot_distance, values, **style)

    def plot_solid(self, ax, solid, extensions, min_thickness=0.):
        distance, top, base = solid.sample(self.cs.shape)
        if (
            (np.isnan(top).all()) or
            (np.nanmax(top) < self.ylim[0]) or
            (np.nanmin(base) > self.ylim[1])
            ):
            self.styles['solids'].remove(solid.stylekey)
            return
        plot_distance = extensions(distance)
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

    def get_extensions(self, distance, min_distance):
        '''x-axis extensions'''
        xp = np.concatenate([[0., ], distance, [self.length,]])
        fp= np.cumsum(
            np.concatenate([xp[:1], np.maximum(np.diff(xp), min_distance)])
            )
        extensions = partial(np.interp, xp=xp, fp=fp)
        return extensions

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

        # borehole distance vector
        borehole_distance = np.array([d for d, b in self.cs.boreholes])

        # x-axis limits
        xmin, xmax = [0., self.length]

        # adjust limits for first and last borehole
        if len(borehole_distance) > 0:
            min_limit_factor = self.cfg.get('min_limit_factor', 4.e-2)
            min_limit = min_limit_factor * self.length
            if borehole_distance[0] < (min_limit):
                xmin -= ((min_limit) - borehole_distance[0])
            if (xmax - borehole_distance[-1]) < (min_limit):
                xmax += ((min_limit) - (xmax - borehole_distance[-1]))

        # get plot_distance and x-axis extensions
        extensions = self.get_extensions(borehole_distance, min_distance)

        # apply extensions to x-axis limits
        # xmax = extensions(xmax)

        # bar & vertical width
        barwidth_factor = self.cfg.get('barwidth_factor', 1.e-2)
        verticalwidth_factor = self.cfg.get('verticalwidth_factor', 1.e-2)
        barwidth = barwidth_factor * (xmax - xmin)
        verticalwidth = verticalwidth_factor * (xmax - xmin)

        # plot boreholes
        for distance, borehole in self.cs.boreholes:

            # plot borehole
            txt = self.plot_borehole(ax, distance, borehole, extensions, barwidth)
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
                    distance=distance,
                    vertical=vertical,
                    extensions=extensions,
                    width=verticalwidth,
                    style=style,
                    )

            if (len(borehole.segments) == 0) and (len(borehole.verticals) > 0):
                key = next(iter(self.styles['verticals'].records.keys()))
                vertical = borehole.verticals[key].relative_to(borehole.z)
                self.plot_edge(
                    ax,
                    distance=distance,
                    vertical=vertical,
                    extensions=extensions,
                    width=verticalwidth,
                    style=self.cfg.get('verticaledge_style') or {},
                    )

        # plot points
        for distance, point in self.cs.points:
            if point.midlevel is None:
                continue
            self.plot_point(ax,
                distance=distance,
                point=point,
                extensions=extensions,
                )

        # well distance vector
        well_distance = np.array([d for d, w in self.cs.wells])

        # get plot_distance and x-axis extensions
        extensions = lambda x: extensions(self.get_extensions(well_distance, min_distance)(x))

        # adjust limits for first and last well
        if len(well_distance) > 0:
            min_limit_factor = self.cfg.get('min_limit_factor', 4.e-2)
            min_limit = min_limit_factor * self.length
            if well_distance[0] < (min_limit):
                xmin -= ((min_limit) - well_distance[0])
            if (xmax - well_distance[-1]) < (min_limit):
                xmax += ((min_limit) - (xmax - well_distance[-1]))

        # apply extensions to x-axis limits
        xmax = extensions(xmax)

        for distance, well in self.cs.wells:
            txt = self.plot_well(ax,
                distance=distance,
                well=well,
                extensions=extensions,
                width=barwidth,
                )
            bxa.append(txt)

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
        extended_xticks = extensions(xticks)
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
