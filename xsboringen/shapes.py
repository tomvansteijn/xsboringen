# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import fiona

import logging
import os

def read(shapefile):
    with fiona.open(shapefile, 'r') as src:
        logging.debug('reading {f:}'.format(f=os.path.basename(shapefile)))
        for row in src:
            yield row
