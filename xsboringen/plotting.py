# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.solid import get_solid_data
from xsboringen.surface import get_surface_data

import matplotlib.patheffects as PathEffects
from matplotlib import pyplot as plt
from matplotlib import transforms
import joblib
import numpy as np

import logging
import os


class Extensions(object):
    def __init__(self, xp, yp):
        self.xp = xp
        self.yp = yp

    def extend(self, x):
        return np.interp(x, xp=self.xp, fp=self.yp)


class CrossSectionPlot(object):
    def __init__(self, cross_section, styles, config,
        xtickstep=None, xlim=None, ylim=None, xlabel=None, ylabel=None, legend_ncol=1,
        ):
        self.cs = cross_section
        self.styles = styles
        self.cfg = config

        self.xtickstep = xtickstep
        self.xlim = xlim or [0., self.cs.shape.length]
        self.ylim = ylim
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend_ncol = legend_ncol

    def __repr__(self):
        return ('{s.__class__.__name__:}(length={s.length:.2f}, '
                'styles={s.styles:}, '
                'label={s.cs.label:})').format(s=self)

    @property
    def xrange_(self):
        xmin, xmax = self.xlim
        return xmax - xmin

    @property
    def min_distance(self):
        # calculate min distance
        min_distance_factor = self.cfg.get('min_distance_factor', 2.e-2)
        return min_distance_factor * self.cs.shape.length

    @property
    def barwidth(self):
        barwidth_factor = self.cfg.get('barwidth_factor', 1.e-2)
        return barwidth_factor * self.xrange_

    @property
    def verticalwidth(self):
        verticalwidth_factor = self.cfg.get('verticalwidth_factor', 1.e-2)
        return verticalwidth_factor * self.xrange_

    @property
    def wellfilterwidth(self):
        wellfilterwidth_factor = self.cfg.get('wellfilterwidth_factor', 1.e-2)
        return wellfilterwidth_factor * self.xrange_

    def adjust_xlim(self, distance):
        xmin, xmax = self.xlim
        if len(distance) > 0:
            min_limit_factor = self.cfg.get('min_limit_factor', 4.e-2)
            min_limit = min_limit_factor * self.cs.shape.length
            if distance[0] < (min_limit):
                xmin -= (min_limit - distance[0])
            if (xmax - distance[-1]) < (min_limit):
                xmax += (min_limit - (xmax - distance[-1]))
        self.xlim = xmin, xmax

    def get_extensions(self, distance):
        '''x-axis extensions'''
        xp = np.concatenate([[0., ], distance, [self.cs.shape.length,]])
        yp = np.cumsum(
            np.concatenate([xp[:1], np.maximum(np.diff(xp), self.min_distance)])
            )
        extensions = Extensions(xp=xp, yp=yp)
        return extensions

    def plot_code(self, ax, distance, code):
        codelabel_position = self.cfg.get('codelabel_position')
        codelabel_fontsize = self.cfg.get('codelabel_fontsize')
        codelabel_color = self.cfg.get('codelabel_color')
        vtrans = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
        txt = ax.text(distance, codelabel_position, code,
            size=codelabel_fontsize,
            color=codelabel_color,
            rotation=90,
            ha='center', va='bottom',
            transform=vtrans,
            )
        return txt

    def plot_label(self, ax):
        if len(self.cs.label.split("_")) > 1:
            leftlabel, rightlabel = self.cs.label.split("_")[1]
        else:
            leftlabel, rightlabel = self.cs.label, self.cs.label + '`'
        ll = ax.text(0, 1.01, leftlabel, weight='bold', size='large',
             transform=ax.transAxes)
        rl = ax.text(1, 1.01, rightlabel, weight='bold', size='large',
             transform=ax.transAxes)
        return ll, rl

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
        if len(self.cs.wells) > 0:
            for label, style in self.styles['wells'].items():
                handles_labels.append((
                    plt.Rectangle((0, 0), 1, 1,
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

    def plot_borehole(self, ax, distance, borehole, extensions, width):
        plot_distance = extensions.extend(distance)
        for segment in borehole:
            height = segment.thickness
            bottom = borehole.z - segment.base
            segment_style = self.styles['segments'].lookup(segment)

            # plot segment as bar
            rect = ax.bar(plot_distance, height, width, bottom,
                align='center', zorder=2,
                **segment_style)

        # plot borehole code as text
        txt = self.plot_code(ax, plot_distance, borehole.code)
        return txt

    def plot_vertical(self, ax, distance, vertical, extensions, width, style):
        plot_distance = extensions.extend(distance)
        depth = np.array(vertical.depth, dtype=np.float)
        rescaled = np.array(vertical.rescaled().values, dtype=np.float)
        transformed = plot_distance + (rescaled - 0.5)*width
        vert = ax.plot(transformed, depth, **style)
        return vert

    def plot_edge(self, ax, distance, vertical, extensions, width, style):
        plot_distance = extensions.extend(distance)
        height = vertical.depth[0] - vertical.depth[-1]
        bottom = vertical.depth[-1]
        # plot edge as bar
        rect = ax.bar(plot_distance, height, width, bottom,
            align='center', zorder=2,
            **style)

    def plot_well(self, ax, distance, well, extensions, width):
        plot_distance = extensions.extend(distance)
        wellfilter = ax.bar(plot_distance, well.filterlength, width, well.z - well.filterbottomlevel,
                align='center', zorder=2,
                **self.styles['wells'].lookup('wellfilter'))
                
        standpipe = ax.plot([plot_distance, plot_distance], [well.z, well.z - well.filtertoplevel],
                zorder=2,
                **self.cfg["standpipe_style"])

        for blind_filtersegment in well.get_blind_filtersegments():
            ax.bar(plot_distance, blind_filtersegment.length, width, well.z - blind_filtersegment.bottomlevel,
                align='center', zorder=3,
                **self.styles['wells'].lookup('blind_filtersegment'))

        # plot well code as text
        txt = self.plot_code(ax, plot_distance, well.code)
        return txt

    def plot_point(self, ax, distance, point, extensions,
        ):
        plot_distance = extensions.extend(distance)
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
        if not surface.has_data:
            distance, values = surface.sample(self.cs.shape) 
        else:
            distance, values = surface.data        
        plot_distance = extensions.extend(distance)
        style = self.styles['surfaces'].lookup(surface.stylekey)
        sf = ax.plot(plot_distance, values, **style)

    def plot_solid(self, ax, solid, extensions, min_thickness=0.):
        if not solid.has_data:
            distance, top, base = solid.sample(self.cs.shape)
        else:
            distance, top, base = solid.data
        if (
            (np.isnan(top).all()) or
            (np.isnan(base).all()) or
            (np.nanmax(top) < self.ylim[0]) or
            (np.nanmin(base) > self.ylim[1])
            ):
            self.styles['solids'].remove(solid.stylekey)
            return
        plot_distance = extensions.extend(distance)
        style = self.styles['solids'].lookup(solid.stylekey)
        sld = ax.fill_between(plot_distance, base, top,
            where=(top - base) > min_thickness,
            **style,
            )

        # top_clip = np.clip(top, self.ylim[0], self.ylim[1])
        # base_clip = np.clip(base, self.ylim[0], self.ylim[1])
        # thickness = (top_clip - base_clip)
        
        # idx = (
        #     ((distance > 0.01 * distance.max()) &
        #     (distance < 0.99 * distance.max())) &
        #     ((distance < (self.cs.wells[0][0] - 0.05 * distance.max())) |
        #     (distance > (self.cs.wells[-1][0] + 0.05 * distance.max()))) & 
        #     (thickness < np.nanquantile(thickness, 0.9))
        #     ).nonzero()

        # if not len(idx[0]) > 0:
        #     return

        # idx = idx[0][thickness[idx].argmax()]
        # labelx = plot_distance[idx]
        # labely = (top_clip[idx] + base_clip[idx]) / 2.
        # txt = ax.text(labelx, labely, solid.name, horizontalalignment="center", verticalalignment="center", size="small")
        # return txt

    def plot(self, ax):
        # bounding box extra artists (title, legend, labels, etc.)
        bxa = []

        # sort cross-section data by distance
        self.cs.sort()

        # borehole distance vector
        borehole_distance = np.array([d for d, b in self.cs.boreholes])

        # well distance vector
        well_distance = np.array([d for d, w in self.cs.wells])

        # combined distance vector
        obj_distance = np.concatenate([borehole_distance, well_distance])
        obj_distance.sort()

        # adjust limits for first and last borehole
        self.adjust_xlim(obj_distance)

        # get plot_distance and x-axis extensions     
        extensions = self.get_extensions(obj_distance)

        # plot boreholes
        for distance, borehole in self.cs.boreholes:

            # plot borehole
            txt = self.plot_borehole(ax, distance, borehole, extensions, self.barwidth)
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
                    width=self.verticalwidth,
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
                    width=self.verticalwidth,
                    style=self.cfg.get('verticaledge_style') or {},
                    )

        # plot wells
        for distance, well in self.cs.wells:
            txt = self.plot_well(ax,
                distance=distance,
                well=well,
                extensions=extensions,
                width=self.wellfilterwidth,
                )
            bxa.append(txt)

        # plot points
        for distance, point in self.cs.points:
            if point.midlevel is None:
                continue
            self.plot_point(ax,
                distance=distance,
                point=point,
                extensions=extensions,
                )

        # plot surfaces
        if self.cfg["n_jobs"] > 1:
            parallel = joblib.Parallel(n_jobs=self.cfg["n_jobs"])
            get_data = joblib.delayed(get_surface_data)
            self.cs.surfaces = parallel(get_data(s, self.cs.geometry) for s in self.cs.surfaces)
        for surface in self.cs.surfaces:
            self.plot_surface(ax,
                surface=surface,
                extensions=extensions,
                )

        # plot solids
        if self.cfg["n_jobs"] > 1:
            parallel = joblib.Parallel(n_jobs=self.cfg["n_jobs"])
            get_data = joblib.delayed(get_solid_data)
            self.cs.solids = parallel(get_data(s, self.cs.geometry) for s in self.cs.solids)
        for solid in self.cs.solids:
            self.plot_solid(ax,
                solid=solid,
                extensions=extensions,
                )

        # plot labels
        if self.cs.label is not None:
            lt, rt = self.plot_label(ax)
            bxa.append(lt)
            bxa.append(rt)

        # axis ticks
        if self.xtickstep is not None:
            xticks = np.arange(0., self.cs.shape.length + self.xtickstep, self.xtickstep)
        else:
            xticks = ax.get_xticks().copy()

        fmt = self.cfg.get('xticklabel_format', '{:3.0f}')
        xticklabels = [fmt.format(x) for x in xticks]
        extended_xticks = extensions.extend(xticks)
        ax.set_xticks(extended_xticks)
        ax.set_xticklabels(xticklabels)

        # axis limits
        xmin, xmax = self.xlim
        xmax = extensions.extend(xmax)
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

        if len(self.cs.label.split("_")) > 1:
            title = self.cs.label.split("_")[0]      
            ttl = ax.set_title(title, weight='bold', size='large', pad=70)

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
