# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.borehole import Borehole

from shapely.geometry import shape, mapping, Point, LineString
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


def boreholes_to_shape(boreholes, shapefile,
        driver=None, epsg=None, fields=None):
    '''write boreholes to shapefile as points'''
    # crs from epsg code
    if epsg is not None:
        crs = from_epsg(epsg)
    else:
        crs = None

    # shapefile schema
    schema = Borehole.schema.copy()
    if fields is not None:
        schema['properties'].extend(fields)

    # shapefile write arguments
    shape_kwargs = {
        'driver': driver,
        'schema': schema,
        'crs': crs,
        }
    keys = [k for k, _ in schema['properties']]
    log.info('writing to {f:}'.format(f=os.path.basename(shapefile)))
    with fiona.open(shapefile, 'w', **shape_kwargs) as dst:
        for borehole in boreholes:
            record = {
                    'geometry': borehole.geometry,
                    'properties': borehole.as_dict(keys=keys),
                }
            dst.write(record)


def export_endpoints(shapefile, cross_sections, driver=None, epsg=None):
    # crs from epsg code
    if epsg is not None:
        crs = from_epsg(epsg)
    else:
        crs = None

    # schema
    schema = {'geometry': 'Point', 'properties': {'label': 'str'}}

    # shapefile write arguments
    shape_kwargs = {
        'driver': driver,
        'schema': schema,
        'crs': crs,
        }
    log.info('writing to {f:}'.format(f=os.path.basename(shapefile)))
    with fiona.open(shapefile, 'w', **shape_kwargs) as dst:
        for cs in cross_sections:
            startpoint = Point(cs.shape.coords[0])
            endpoint = Point(cs.shape.coords[-1])
            dst.write({
                'geometry': mapping(startpoint),
                'properties': {'label': cs.label}
                })
            dst.write({
                'geometry': mapping(endpoint),
                'properties': {'label': cs.label + '`'}
                })


def export_projectionlines(shapefile, cross_sections, driver=None, epsg=None):
    # crs from epsg code
    if epsg is not None:
        crs = from_epsg(epsg)
    else:
        crs = None

    # schema
    schema = {'geometry': 'LineString', 'properties': {'label': 'str'}}
    boreholeschema = Borehole.schema.copy()
    schema['properties'].update(boreholeschema['properties'])
    keys = [k for k, _ in boreholeschema['properties']]

    # shapefile write arguments
    shape_kwargs = {
        'driver': driver,
        'schema': schema,
        'crs': crs,
        }

    log.info('writing to {f:}'.format(f=os.path.basename(shapefile)))
    with fiona.open(shapefile, 'w', **shape_kwargs) as dst:
        for cs in cross_sections:
            for distance, borehole in cs.boreholes:
                projectionline = LineString([
                    shape(borehole.geometry),
                    cs.shape.interpolate(distance),
                    ])
                properties = {'label': cs.label}
                properties.update(borehole.as_dict(keys=keys))
                dst.write({
                    'geometry': mapping(projectionline),
                    'properties': properties,
                    })
