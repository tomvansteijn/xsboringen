# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen import config

from matplotlib import pyplot as plt


class CrossSectionPlot(object):
    def __init__(self, cross_section, styles,
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

         # internal
        self.bxa = []

    def get_style(self, segment):
        return self.styles.lookup(segment)

    def __repr__(self):
        return ('{s.__class__.__name__:}(length={s.length:.2f}, '
                'styles={s.styles:}, '
                'label={s.label:})').format(s=self)

    @staticmethod
    def plot_borehole(ax, left, borehole, width):
        for segment in borehole:
            height = segment.thickness
            bottom = borehole.z - segment.base
            style = self.get_style(segment)
            rect = ax.bar(left, width, height, bottom,
                align='center', zorder=2,
                **style)

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
        self.bxa = []

        barwidth = self.get_barwidth()
        # plot boreholes
        for distance, borehole in self.cs.boreholes:
            self.plot_borehole(ax, distance, borehole, barwidth)

        # plot wells

        # plot points

        # plot lines

        # plot solids

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
        self.bxa.append(lgd)

    def save(imagefile, **save_kwargs):
        # plot
        self.plot()

        # save figure
        plt.savefig(imagefile,
            bbox_inches='tight',
            bbox_extra_artists=self.bxa,
            **save_kwargs,
            )
