# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.objects import Borehole, Segment, CPT

from xml.etree import ElementTree
import datetime
import logging
import os


def safe_int(s, int):
    try:
        return int(s)
    else:
        return None


def safe_float(s):
    try:
        return float(s)
    else:
        return None


def segments_from_xml(root):
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

        # organic matter content
        fields = {}
        try:
            fields['organic_matter'] = safe_float(interval.find(
                'organMatPerc').attrib.get('percentage'))
        except AttributeError:
            fields['organic_matter'] = None

        # yield segment
        yield Segment(top, base, lithology,
            sandmedianclass=sandmedianclass,
            fields=fields,
            )


def borehole_from_xml(xmlfile):
    '''read Dinoloket XML file and return Borehole'''
    logging.debug('reading {file:}'.format(file=os.path.basename(xmlfile)))
    fields = {}
    fields['source'] = xmlfile

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
            fields['date'] = datetime.datetime(year, month, day).isoformat()
        elif year and month:
            fields['date'] = datetime.datetime(year, month, 1).isoformat()
        elif year:
            fields['date'] = datetime.datetime(year, 1, 1).isoformat()
        else:
            fields['date'] = None
    except AttributeError:
        fields['date'] = None

    # final depth of borehole in m
    basedepth = survey.find('borehole').attrib.get('baseDepth')
    depth = safe_float(basedepth) * 1e-2  # to m

    # x,y coordinates
    coordinates = survey.find('surveyLocation/coordinates')
    x = safe_float(coordinates.find('coordinateX').text)
    y = safe_float(coordinates.find('coordinateY').text)

    # elevation in m
    elevation = survey.find('surfaceElevation/elevation')
    if not elevation is None:
        z = safe_float(elevation.attrib.get('levelValue')) * 1e-2  # to m
    else:
        z = None

    # segments as generator
    segments = partial(segments_from_xml, root=root)

    return Borehole(code, depth,
        fields=fields,
        x=x, y=y, z=z,
        segments=segments,
        )
