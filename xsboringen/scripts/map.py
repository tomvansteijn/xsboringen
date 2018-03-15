#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen import plotting
from xsboringen import shapefiles

import yaml

from pathlib import Path
import logging
import os

log = logging.getLogger(os.path.basename(__file__))


def plot_map(**kwargs):
    # args
    datasources = kwargs['datasources']
    cross_section_lines = kwargs['cross_section_lines']
    result = kwargs['result']
    config = kwargs['config']

    css = []
    for row in shapefiles.read(cross_section_lines['file']):
        plt = plotting.MapPlot(

            )

