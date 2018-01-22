# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.borehole import Borehole, Segment

from itertools import chain
from xml.etree import ElementTree
import datetime
import logging
import glob
import csv
import os

log = logging.getLogger(os.path.basename(__file__))


def boreholes_from_xml(folder, version):
    xmlfiles = glob.glob(os.path.join(folder, '*{:.1f}.xml'.format(version)))
    for xmlfile in xmlfiles:
        yield borehole_from_xml(xmlfile)


def safe_int(s):
    try:
        return int(s)
    except TypeError:
        return None


def safe_float(s):
    try:
        return float(s)
    except TypeError:
        return None


def segments_from_xml(root, extra_fields=None):
    '''read segments from XML and yield as Segment'''
    intervals = root.findall('pointSurvey/borehole/lithoDescr/lithoInterval')
    for interval in intervals:
        # top and base
        top = safe_float(interval.attrib.get('topDepth')) * 1e-2  # to m
        base = safe_float(interval.attrib.get('baseDepth')) * 1e-2  # to m

        # lithology
        lithology = interval.find('lithology').attrib.get('code')

        # sandmedianclass
        try:
            sandmedianclass = interval.find(
                'sandMedianClass').attrib.get('code')[:3]
        except AttributeError:
            sandmedianclass = None

        # sand median
        try:
            sandmedian = safe_float(interval.find(
                'sandMedian').attrib.get('median'))
        except AttributeError:
            sandmedian = None

        # extra fields
        attrs = {}
        if extra_fields is not None:
            for key, attr in fields:
                element = interval.find(key)
                if element is not None:
                    attrs[key] = element.attrib.get(attr)

        # yield segment
        yield Segment(top, base, lithology,
            sandmedianclass=sandmedianclass,
            **attrs,
            )


def borehole_from_xml(xmlfile, extra_fields=None):
    '''read Dinoloket XML file and return Borehole'''
    log.debug('reading {file:}'.format(file=os.path.basename(xmlfile)))
    attrs = {}
    attrs['source'] = xmlfile

    tree = ElementTree.parse(xmlfile)
    root = tree.getroot()

    # code
    survey = root.find('pointSurvey')
    code = survey.find('identification').attrib.get('id')

    # date of borehole
    date = survey.find('borehole/date')
    try:
        year = safe_int(date.attrib.get('startYear'))
        month = safe_int(date.attrib.get('startMonth'))
        day = safe_int(date.attrib.get('startDay'))
        if year and month and day:
            attrs['date'] = datetime.datetime(year, month, day).isoformat()
        elif year and month:
            attrs['date'] = datetime.datetime(year, month, 1).isoformat()
        elif year:
            attrs['date'] = datetime.datetime(year, 1, 1).isoformat()
        else:
            attrs['date'] = None
    except AttributeError:
        attrs['date'] = None

    # final depth of borehole in m
    basedepth = survey.find('borehole').attrib.get('baseDepth')
    depth = safe_float(basedepth)
    try:
        depth *= 1e-2  # to m
    except TypeError:
        depth = None

    # x,y coordinates
    coordinates = survey.find('surveyLocation/coordinates')
    x = safe_float(coordinates.find('coordinateX').text)
    y = safe_float(coordinates.find('coordinateY').text)

    # elevation in m
    elevation = survey.find('surfaceElevation/elevation')
    if not elevation is None:
        z = safe_float(elevation.attrib.get('levelValue'))
        try:
            z *= 1e-2  # to m
        except TypeError:
            z = None
    else:
        z = None

    # segments as generator
    segments = segments_from_xml(root, extra_fields)

    return Borehole(code, depth,
        x=x, y=y, z=z,
        segments=segments,
        **attrs,
        )
