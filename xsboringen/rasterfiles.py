# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from shapely.geometry import Point
from rasterio import features

import rasterio
import numpy as np

from functools import partial
import logging
import os

log = logging.getLogger(os.path.basename(__file__))

# rio.DatasetReader.sample method does not work when trying to sample  
# outside of the raster's spaial extent. This is a workaround.
def take_rio_sample(dataset, coords):
    ''' take sample from raster workaround method (simplified without rasterio.windows.Window) 
    it yields np.nan if you look outside of the raster's spatial extent'''
    for x,y in coords:
        ix, iy = dataset.index(x, y)
        if ix < dataset.shape[0] and ix >= 0 and iy < dataset.shape[1] and iy >= 0:
            yield [dataset.read()[0, ix, iy]]
        else:
            yield [np.nan]


def sample_raster(rasterfile, coords):
    '''sample raster file at coords'''
    log.debug('reading rasterfile {}'.format(os.path.basename(rasterfile)))
    with rasterio.open(rasterfile) as src:
        for value in take_rio_sample(src, coords):
            if value[0] in src.nodatavals:
                yield np.nan
            elif np.isnan(value[0]) and any(np.isnan(src.nodatavals)):
                yield np.nan
            else:
                yield float(value[0])


def sample_linestring(rasterfile, linestring):
    '''sample raster file at coords'''
    log.info('reading rasterfile {}'.format(os.path.basename(rasterfile)))        
    with rasterio.open(rasterfile) as src:
        shapes = [(linestring, 1),]
        values = src.read(1, masked=True)
        is_line = rasterio.features.rasterize(shapes,
            out_shape=src.shape,
            transform=src.transform,
            all_touched=True,
            dtype=np.int16,
            ).astype(np.bool)
        res = src.res[0]
    
    # get array values along line
    array_values = values.filled(np.nan)[is_line]

    # get midpoint x, y coordinates
    rows, cols = np.where(is_line)
    xs, ys = rasterio.transform.xy(src.transform, rows, cols)
    midpoints = [Point(x, y) for x, y in zip(xs, ys)]

    # sort by distance of midpoint along line    
    by_midpoint_distance = lambda pv: linestring.project(pv[0])
    midpoints_values = sorted(zip(midpoints, array_values), key=by_midpoint_distance)

    distance = []
    values = []
    for midpoint, value in midpoints_values:
        square = midpoint.buffer(res / 2).envelope
        itc_line = linestring.intersection(square)      
        itc_pnts = [Point(x, y) for x, y in itc_line.coords]
        itc_distance = [linestring.project(p) for p in itc_pnts]
        distance.extend(itc_distance)
        values.extend([value for d in itc_distance])        
    distance = np.array(distance)
    values = np.array(values)
    return distance, values
