# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from matplotlib import pyplot as plt

def plot_borehole(ax, borehole):
    for segment in borehole:
        pass


def plot_solid(ax, solid):
    pass


def plot_cross_section(cross_section, imagefile,
    styles=None, figsize=None, ylim=None, xlabel=None, ylabel=None):

    fig, ax = plt.subplots(figsize=figsize)
    bxa = []

    # plot boreholes

    # plot wells

    # plot points

    # plot lines

    # plot solids

    # axis limits
    ax.set_xlim([0., AsShape(cross_section.geometry).length])
    if ylim is not None:
        ax.set_ylim(ylim)

    # grid lines |--|--|--|
    ax.grid()

    # axis labels
    if xlabel is not None:
        ax.set_xlabel(xlabel)

    if ylabel is not None:
        ax.set_ylabel(ylabel)

    # legend
    lgd = ax.legend()
    bxa.append(lgd)

    # save figure
    plt.savefig(imagefile, bbox_inches='tight', bbox_extra_artists=bxa)
