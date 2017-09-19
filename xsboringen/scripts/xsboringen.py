# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen import config
from xsboringen import cross_section
from xsboringen import files
from xsboringen import plot as xsplot
from xsboringen import shapes as xshapes
from xsboringen import styles as xstyles

import yaml

import argparse
import logging
import os


def plot(**kwargs):
    # args
    datafolders = kwargs['datafolders']
    lineshape = kwargs['lineshapefile']
    result = kwargs['result']

    # optional args
    min_depth = kwargs.get('min_depth', 0.)
    buffer_distance = kwargs.get('buffer_distance', 0.)
    ylim = kwargs.get('ylim')
    xlabel = kwargs.get('xlabel')
    ylabel = kwargs.get('ylabel')
    styles = kwargs.get('styles', config.STYLES)

    # create output folder
    if not os.path.exists(result['folder']):
        os.mkdir(result['folder'])

    # read boreholes and CPT's from data folders
    boreholes = files.from_folders(datafolders)
    boreholes = [
        b for b in boreholes
        if (b.x is not None) and (b.y is not None) and (b.z is not None) and
        (b.depth >= min_depth)
        ]

    # define styles lookup
    styles = xstyles.StylesLookup(**styles)

    for line_geometry, line_properties in xshapes.read(lineshape['file']):
        # get label
        if lineshape['labelfield'] is not None:
            label = line_properties[lineshape['labelfield']]
        else:
            label = next(config.LABELS)

        # log message
        logging.info('cross-section {label:}'.format(label=label))

        # define cross-section
        cs_kwargs = {
            'geometry': line_geometry,
            'label': label,
            'buffer_distance': buffer_distance,
            }
        cs = cross_section.CrossSection(**cs_kwargs)

        # add boreholes to cross-section
        cs.add_boreholes(boreholes)

        # define plot
        plot_kwargs = {
            'cross_section': cs,
            'styles': styles,
            'ylim': ylim,
            'xlabel': xlabel,
            'ylabel': ylabel,
            }
        plt = xsplot.CrossSectionPlot(**plot_kwargs)

        # plot and save to file
        imagefile = os.path.join(resultfolder,
            config.IMAGEFILEFORMAT.format(label=label))
        plt.save(imagefile)


def get_parser():
    '''get argumentparser and add arguments'''
    parser = argparse.ArgumentParser(
        'plot geological profiles',
        )

    # Command line arguments
    parser.add_argument('function', type=str,
            help=('YAML input file containing keyword arguments'))
    parser.add_argument('inputfile', type=str,
        help=('YAML input file containing keyword arguments'))
    return parser

def main():
    # arguments from input file
    args = get_parser().parse_args()
    with open(args.inputfile) as y:
        kwargs = yaml.load(y)
        kwargs['inputfile'] = args.inputfile
    plot(**kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
