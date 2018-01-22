#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.csvfiles import boreholes_from_csv
from xsboringen.geffiles import boreholes_from_gef
from xsboringen.xmlfiles import boreholes_from_xml

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
        elif datasource['format'] == 'Dinoloket GEF':
            folder = datasource['folder']
            readers.append(boreholes_from_gef(
                folder=folder,
                delimiter=datasource.get('delimiter', ','),
                ))
        else:
            pass
    for result in chain(*readers):
        yield result
