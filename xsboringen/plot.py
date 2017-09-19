# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen import config

from matplotlib import pyplot as plt
from matplotlib import transforms

import logging
import os


class CrossSectionPlot(object):
    def __init__(self, cross_section, styles, config,
        ylim=None,
        xlabel=None, ylabel=None, label=None,
        figsize=None, pages=None,
        ):
        self.cs = cross_section
        self.styles = styles

        self.ylim = ylim

        self.xlabel = xlabel
        self.ylabel = ylabel
        self.label = label

        self.figsize = figsize or config.FIGSIZE
        self.pages = pages or 1

    def get_style(self, segment):
        return self.styles.lookup(segment)

    def __repr__(self):
        return ('{s.__class__.__name__:}(length={s.length:.2f}, '
                'styles={s.styles:}, '
                'label={s.label:})').format(s=self)

    def plot_borehole(self, ax, left, borehole, width):
        vtrans = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
        for segment in borehole:
            height = segment.thickness
            bottom = borehole.z - segment.base
            segment_style = self.get_style(segment)

            # plot segment as bar
            rect = ax.bar(left, width, height, bottom,
                align='center', zorder=2,
                **segment_style)

            # plot borehole code as text
            txt = ax.text(left, config.CODE_POSITION, borehole.code,
                size=config.FONT_SIZE,
                color='gray',
                rotation=90,
                ha='center', va='bottom',
                transform=vtrans,
                )

            yield rect, txt

    def plot_label(ax):
        ax.text(0, 1.01, self.label, weight='bold', size='large',
             transform=ax.transAxes)
        ax.text(1, 1.01, self.label + '`', weight='bold', size='large',
             transform=ax.transAxes)

    def get_barwidth(self):
        '''bar width from cross-section length'''
        barwidth = self.cs.length * config.PLOT_BARWIDTH
        if self.pages > 1:
            barwidth /= self.pages
        return barwidth

    def get_xlim(self):
        return [0., self.cs.length]

    def plot(self):
        fig, ax = plt.subplots(figsize=figsize)
        bxa = []

        barwidth = self.get_barwidth()

        # plot boreholes
        for distance, borehole in self.cs.boreholes:
            for rect, txt in self.plot_borehole(ax,
                    distance, borehole, barwidth,
                    ):
                bxa.append(txt)

        # plot wells

        # plot points

        # plot lines

        # plot solids

        # plot labels
        self.plot_label(ax)

        # axis limits
        ax.set_xlim(self.get_xlim())
        if self.ylim is not None:
            ax.set_ylim(self.ylim)

        # grid lines |--|--|--|
        ax.grid()

        # axis labels
        if self.xlabel is not None:
            ax.set_xlabel(self.xlabel)

        if self.ylabel is not None:
            ax.set_ylabel(self.ylabel)

        # legend
        lgd = ax.legend()
        bxa.append(lgd)

        return bxa

    def save(imagefile, **save_kwargs):
        # plot
        bxa = self.plot()

        # save figure
        logging.info('saving {:f}'.format(os.path.basename(imagefile)))
        plt.savefig(imagefile,
            bbox_inches='tight',
            bbox_extra_artists=bxa,
            **save_kwargs,
            )
