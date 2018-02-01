# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen import cross_section
from xsboringen.csvfiles import boreholes_to_csv
from xsboringen.datasources import boreholes_from_sources
from xsboringen import plot as xsplot
from xsboringen import shapefiles
from xsboringen import styles

import click
import yaml

from collections import ChainMap
import logging
import os

log = logging.getLogger(os.path.basename(__file__))


def write_csv(**kwargs):
    # args
    datasources = kwargs['datasources']
    result = kwargs['result']
    config = kwargs['config']

    # read boreholes and CPT's from data folders
    boreholes = boreholes_from_sources(datasources)

    # simplify if needed
    if result.get('simplify', False):
        min_thickness = result.get('min_thickness')
        boreholes = (
            b.simplified(min_thickness=min_thickness) for b in boreholes
            )

    # classify sandmedian if needed

    # translate CPT to lithology if needed

    # write output to csv
    boreholes_to_csv(boreholes, result['csvfile'])


def write_shape(**kwargs):
    # args
    datasources = kwargs['datasources']
    result = kwargs['result']
    config = kwargs['config']

    # read boreholes and CPT's from data folders
    boreholes = boreholes_from_sources(datasources)

    # simplify if needed
    if result.get('simplify', False):
        min_thickness = result.get('min_thickness')
        boreholes = (
            b.simplified(min_thickness=min_thickness) for b in boreholes
            )

    # write output to shapefile
    driver = config.get('shapefile.driver')
    epsg = config.get('shapefile.epsg')
    shapefiles.boreholes_to_shape(boreholes, result['shapefile'],
        **config['shapefile'],
        )


def plot(**kwargs):
    # args
    datasources = kwargs['datasources']
    lines = kwargs['lines']
    result = kwargs['result']
    config = kwargs['config']

    # optional args
    min_depth = kwargs.get('min_depth', 0.)
    buffer_distance = kwargs.get('buffer_distance', 0.)
    ylim = kwargs.get('ylim')
    xlabel = kwargs.get('xlabel')
    ylabel = kwargs.get('ylabel')

    # create image folder
    if result.get('imagefolder') and not os.path.exists(result['imagefolder']):
        os.mkdir(result['imagefolder'])

    # read boreholes and CPT's from data folders
    boreholes = boreholes_from_sources(datasources)

    # simplify if needed
    if result.get('simplify', False):
        min_thickness = result.get('min_thickness')
        boreholes = (
            b.simplified(min_thickness=min_thickness) for b in boreholes
            )

    # filter missing coordinates and less than minimal depth
    boreholes = [
        b for b in boreholes
        if (b.x is not None) and (b.y is not None) and (b.z is not None) and
        (b.depth >= min_depth)
        ]

    # definest yles lookup
    plotting_styles = {
        'segments': styles.ObjectStylesLookup(**config['styles']['segments']),
        # 'points': xstyles.SimpleStylesLookup(**config['point.styles'])
        }

    # default labels
    defaultlabels = iter(config['cross_section.labels'])

    for row in shapefiles.read(lines['file']):
        line_geometry = row['geometry']
        line_properties = row['properties']

        # get label
        if lines.get('labelfield') is not None:
            label = line_properties[lines['labelfield']]
        else:
            label = next(defaultlabels)

        # log message
        log.info('cross-section {label:}'.format(label=label))

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
            'config': config['plot.config'],
            'styles': styles,
            'ylim': ylim,
            'xlabel': xlabel,
            'ylabel': ylabel,
            }
        plt = xsplot.CrossSectionPlot(**plot_kwargs)

        # plot and save to file
        imagefile = os.path.join(result['imagefolder'],
            config['image.filenameformat'].format(label=label))
        log.info('saving {f:}'.format(f=os.path.basename(imagefile)))
        plt.save(imagefile)


def get_logging(level):
    return {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        }.get(level, logging.DEBUG)


@click.command()
@click.argument('function',
    type=click.Choice(['write_csv', 'write_shape', 'plot']),
    )
@click.argument('inputfile',
    )
@click.option('--logging', 'logging_level',
    type=click.Choice(['warning', 'info', 'debug']),
    default='info',
    help='log messages level'
    )
def main(function, inputfile, logging_level):
    '''plot geological cross-sections'''
    logging.basicConfig(level=get_logging(logging_level))

    # function arguments from input file
    with open(inputfile) as y:
        f_kwargs = yaml.load(y)

    # read default config
    scripts_folder = os.path.dirname(os.path.realpath(__file__))
    defaultconfigfile = os.path.join(os.path.dirname(scripts_folder),
        'defaultconfig.yaml')
    with open(defaultconfigfile) as y:
        defaultconfig = yaml.load(y)

    # get user config from input file
    userconfig = f_kwargs.get('config') or {}

    # chain config
    f_kwargs['config'] = ChainMap(userconfig, defaultconfig)

    # dispatch function
    if function == 'write_csv':
        write_csv(**f_kwargs)
    elif function == 'write_shape':
        write_shape(**f_kwargs)
    elif function == 'plot':
        plot(**f_kwargs)


if __name__ == '__main__':
    main()
