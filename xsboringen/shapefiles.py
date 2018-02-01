# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.borehole import Borehole

from shapely.geometry import mapping
from fiona.crs import from_epsg
import fiona

import logging
import os

log = logging.getLogger(os.path.basename(__file__))


def read(shapefile):
    log.debug('reading {f:}'.format(f=os.path.basename(shapefile)))
    with fiona.open(shapefile, 'r') as src:
        for row in src:
            yield row


def boreholes_to_shape(boreholes, shapefile, driver=None, epsg=None):
    '''write boreholes to shapefile as points'''
    # crs from epsg code
    if epsg is not None:
        crs = from_epsg(epsg)
    else:
        crs = None

    # shapefile schema
    schema = Borehole.schema.copy()
    schema['properties'].extend([('format', 'str'), ('source', 'str')])

    # shapefile write arguments
    shape_kwargs = {
        'driver': driver,
        'schema': schema,
        'crs': crs,
        }
    properties = [k for k, _ in schema['properties']]
    log.info('writing to {f:}'.format(f=os.path.basename(shapefile)))
    with fiona.open(shapefile, 'w', **shape_kwargs) as dst:
        for borehole in boreholes:
            record = {
                    'geometry': borehole.geometry,
                    'properties': borehole.as_dict(keys=properties),
                }
            dst.write(record)
