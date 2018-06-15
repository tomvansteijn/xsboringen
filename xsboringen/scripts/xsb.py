# -*- coding: utf-8 -*-
# Royal HaskoningDHV

from xsboringen.scripts.write_csv import write_csv
from xsboringen.scripts.write_shape import write_shape
from xsboringen.scripts.plot import plot_cross_section

import click
import yaml

from collections import ChainMap
import logging
import os

log = logging.getLogger(os.path.basename(__file__))


@click.command()
@click.argument('function',
    type=click.Choice(['write_csv', 'write_shape', 'plot']),
    )
@click.argument('inputfile',
    )
@click.option('--logging', 'level',
    type=click.Choice(['warning', 'info', 'debug']),
    default='info',
    help='log messages level'
    )
def main(function, inputfile, level):
    '''plot geological cross-sections'''
    logging.basicConfig(level=level.upper())

    # function arguments from input file
    with open(inputfile) as y:
        kwargs = yaml.load(y)

    # read default config
    scripts_folder = os.path.dirname(os.path.realpath(__file__))
    defaultconfigfile = os.path.join(os.path.dirname(scripts_folder),
        'defaultconfig.yaml')
    with open(defaultconfigfile) as y:
        defaultconfig = yaml.load(y)

    # get user config from input file
    userconfig = kwargs.get('config') or {}

    # chain config
    kwargs['config'] = ChainMap(userconfig, defaultconfig)

    # dispatch function
    if function == 'write_csv':
        write_csv(**kwargs)
    elif function == 'write_shape':
        write_shape(**kwargs)
    elif function == 'plot':
        plot_cross_section(**kwargs)

if __name__ == '__main__':
    main()
