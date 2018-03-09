#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.datasources import boreholes_from_sources
from xsboringen import shapefiles

import logging
import os

log = logging.getLogger(os.path.basename(__file__))


def write_shape(**kwargs):
    # args
    datasources = kwargs['datasources']
    result = kwargs['result']
    config = kwargs['config']

    # read boreholes and CPT's from data folders
    borehole_sources = datasources.get('boreholes') or []
    boreholes = boreholes_from_sources(borehole_sources)

    # write output to shapefile
    shape_fields=result.get('shape_fields') or []
    shapefiles.boreholes_to_shape(boreholes, result['shapefile'],
        fields=shape_fields,
        **config['shapefile'],
        )
