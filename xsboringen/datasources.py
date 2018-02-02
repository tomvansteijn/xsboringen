#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.csvfiles import boreholes_from_csv
from xsboringen.geffiles import boreholes_from_gef, cpts_from_gef
from xsboringen.xmlfiles import boreholes_from_xml

from itertools import chain
import logging
import os

log = logging.getLogger(os.path.basename(__file__))

def boreholes_from_sources(datasources):
    readers = []
    for datasource in datasources:
        if datasource['format'] == 'Dinoloket XML 1.4':
            readers.append(boreholes_from_xml(
                folder=datasource['folder'],
                version=1.4,
                extra_fields=datasource.get('extra_fields'),
                ))
        elif datasource['format'] == 'CSV boringen':
            readers.append(boreholes_from_csv(
                folder=datasource['folder'],
                fieldnames=datasource['fieldnames'],
                extra_fields=datasource.get('extra_fields'),
                delimiter=datasource.get('delimiter', ','),
                decimal=datasource.get('decimal', '.'),
                ))
        elif datasource['format'] == 'GEF boringen':
            readers.append(boreholes_from_gef(
                folder=datasource['folder'],
                fieldnames=datasource.get('fieldnames'),
                ))
        elif datasource['format'] == 'GEF sonderingen':
            readers.append(cpts_from_gef(
                folder=datasource['folder'],
                fieldnames=datasource.get('fieldnames'),
                datacolumns=datasource['datacolumns'],
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
