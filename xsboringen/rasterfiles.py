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


def sample_raster(rasterfile, coords, bounds_warning):
    '''sample raster file at coords'''
    log.debug('reading rasterfile {}'.format(os.path.basename(rasterfile)))
    with rasterio.open(rasterfile) as src:
        for value in src.sample(coords, bounds_warning=bounds_warning):
            if value[0] in src.nodatavals:
                yield np.nan
            else:
                yield float(value[0])


def sample_idf(idffile, coords, bounds_warning=True):
    '''sample IDF file at coords'''
    log.debug('reading idf file {}'.format(os.path.basename(idffile)))
    with idfpy.open(idffile) as src:
        for value in src.sample(coords, bounds_warning=bounds_warning):
            if value[0] in src.nodatavals:
                yield np.nan
            else:
                yield float(value[0])


def sample(gridfile, coords, bounds_warning=False):
    '''sample gridfile at coords'''
    if idfpy_imported and gridfile.lower().endswith('.idf'):
        sample = partial(sample_idf, bounds_warning=bounds_warning)
    else:
        sample = partial(sample_raster, bounds_warning=bounds_warning)
    return sample(gridfile, coords)
