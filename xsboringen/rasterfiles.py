# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

try:
    import idfpy
    idfpy_imported = True
except ImportError:
    idfpy_imported = False

import rasterio
import numpy as np

from functools import partial
import logging
import os

log = logging.getLogger(os.path.basename(__file__))


def sample_raster(rasterfile, coords):
    '''sample raster file at coords'''
    log.debug('reading rasterfile {}'.format(os.path.basename(rasterfile)))
    with rasterio.open(rasterfile) as src:
        for value in src.sample(coords):
            if value[0] in src.nodatavals:
                yield np.nan
            else:
                yield float(value[0])


def sample_idf(idffile, coords, boundless=True):
    '''sample IDF file at coords'''
    log.debug('reading idf file {}'.format(os.path.basename(idffile)))
    with idfpy.open(idffile) as src:
        for value in src.sample(coords, boundless=boundless):
            if value[0] in src.nodatavals:
                yield np.nan
            else:
                yield float(value[0])


def sample(gridfile, coords, boundless=True):
    '''sample gridfile at coords'''
    if idfpy_imported and gridfile.lower().endswith('.idf'):
        sample = partial(sample_idf, boundless=True)
    else:
        sample = partial(sample_raster)
    return sample(gridfile, coords)
