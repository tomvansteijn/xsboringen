# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import fiona

import logging

def read(shapefile):
    with fiona.open(shapefile, 'r') as src:
        for row in src:
            yield row
