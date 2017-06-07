# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import yaml

import argparse
import logging

def write_shape(**kwargs):


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
    if
        write_shape(**kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
