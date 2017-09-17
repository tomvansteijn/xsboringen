# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsb import cross_section
from xsb import files
from xsb import plot
from xsb import shapes

import yaml

import argparse
import logging
import os

LABELS = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
IMAGEFILEFORMAT = 'cross_section_{label:}.png'

def plot(**kwargs):
    folders = kwargs.get('folders')
    solids = kwargs.get('solids')
    lineshapefile = kwargs['lineshapefile']
    buffer_distance = kwargs.get('buffer_distance', 0.)
    min_depth = kwargs.get('min_depth', 0.)
    labelfield = kwargs.get('labelfield')
    resultfolder = kwargs['resultfolder']
    ylim = kwargs.get('ylim')
    xlabel = kwargs.get('xlabel')
    ylabel = kwargs.get('ylabel')

    if not os.path.exists(resultfolder):
        os.mkdir(resultfolder)

    folder_kwargs = {
        'folders': folders,
        }

    boreholes = files.from_folders(**folder_kwargs)
    boreholes = [
        b for b in boreholes if b.has_xy and b.has_z and
        (b.depth >= min_depth)
        ]

    for line_geometry, line_properties in shape.read(lineshapefile):
        if labelfield is not None:
            label = line_properties[labelfield]
        else:
            label = next(LABELS)

        cs_kwargs = {
            'geometry': line_geometry,
            'label': label,
            'buffer_distance': buffer_distance,
            }

        cs = cross_section.Cross_Section(**cs_kwargs)

        cs.add_boreholes(boreholes)
        cs.add_solids(solids)

        imagefile = os.path.join(resultfolder,
            IMAGEFILEFORMAT.format(label=label))

        plot_kwargs = {
            'cross_section': cs,
            'imagefile': imagefile,
            'styles': styles,
            'ylim': ylim,
            'xlabel': xlabel,
            'ylabel': ylabel,
            }

        plot.plot_cross_section(**plot_kwargs)


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
