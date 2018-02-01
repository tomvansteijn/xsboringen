#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.csvfiles import boreholes_from_csv
from xsboringen.geffiles import boreholes_from_gef
from xsboringen.geffiles import cpts_from_gef
from xsboringen.xmlfiles import boreholes_from_xml

from itertools import chain
import logging
import os

log = logging.getLogger(os.path.basename(__file__))

def boreholes_from_sources(datasources):
    readers = []
    for datasource in datasources:
        if datasource['format'] == 'Dinoloket XML 1.4':
            folder = datasource['folder']
            readers.append(boreholes_from_xml(
                folder=folder,
                version=1.4,
                ))
        elif datasource['format'] == 'CSV':
            folder = datasource['folder']
            readers.append(boreholes_from_csv(
                folder=folder,
                delimiter=datasource.get('delimiter', ','),
                decimal=datasource.get('decimal', '.'),
                ))
        elif datasource['format'] == 'GEF boringen':
            folder = datasource['folder']
            fieldnames = datasource.get('fieldnames')
            readers.append(boreholes_from_gef(
                folder=folder,
                fieldnames=fieldnames,
                ))
        elif datasource['format'] == 'GEF sonderingen':
            folder = datasource['folder']
            fieldnames = datasource.get('fieldnames')
            readers.append(cpts_from_gef(
                folder=folder,
                fieldnames=fieldnames,
                column_names=datasource['column_names'],
                ))
        else:
            log.warning((
                'dataformat \'{fmt:}\' not supported, skipping').format(
                    fmt=datasource['format'],
                    )
                )
            pass
    for result in chain(*readers):
        yield result
