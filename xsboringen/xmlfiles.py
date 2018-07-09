# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.borehole import Borehole, Segment
from xsboringen import utils

from itertools import chain
from xml.etree import ElementTree
from pathlib import Path
import datetime
import logging
import glob
import csv
import os

log = logging.getLogger(os.path.basename(__file__))


def boreholes_from_xml(folder, version, extra_fields):
    xmlfiles = utils.careful_glob(folder, '*{:.1f}.xml'.format(version))
    for xmlfile in xmlfiles:
        xml = XMLBoreholeFile(xmlfile)
        borehole = xml.to_borehole(extra_fields)
        if borehole is not None:
            yield borehole


class XMLFile(object):
    # format field
    _format = None

    def __init__(self, xmlfile):
        self.file = Path(xmlfile)
        self.attrs = {
            'source': str(self.file),
            'format': self._format,
            }

        log.debug('reading {s.file.name:}'.format(s=self))
        self.root = ElementTree.parse(xmlfile).getroot()


class XMLBoreholeFile(XMLFile):
    _format = 'XML Borehole'

    @staticmethod
    def safe_int(s):
        try:
            return int(s)
        except TypeError:
            return None

    @staticmethod
    def safe_float(s):
        try:
            return float(s)
        except TypeError:
            return None

    @classmethod
    def cast(cls, s, dtype):
        if dtype == 'float':
            return cls.safe_float(s)
        elif dtype == 'int':
            return cls.safe_int(s)
        else:
            return s

    @classmethod
    def read_segments(cls, survey, fields=None):
        '''read segments from XML and yield as Segment'''
        fields = fields or {}
        intervals = survey.findall('borehole/lithoDescr/lithoInterval')
        for interval in intervals:
            # top and base
            top = cls.safe_float(interval.attrib.get('topDepth')) * 1e-2  # to m
            base = cls.safe_float(interval.attrib.get('baseDepth')) * 1e-2  # to m

            # attrs
            attrs = {}

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
                attrs['sandmedian'] = cls.safe_float(interval.find(
                    'sandMedian').attrib.get('median'))
            except AttributeError:
                attrs['sandmedian'] = None

            for field in fields:
                path, attrib = field['match'].split('@')
                element = interval.find(path.rstrip('/'))
                if element is None:
                    continue
                value = element.attrib.get(attrib)
                if value is None:
                    continue
                attrs[field['name']] = cls.cast(value, field['dtype'])

            # yield segment
            yield Segment(top, base, lithology, sandmedianclass, **attrs)

    @staticmethod
    def depth_from_segments(segments):
        log.debug('calculating depth from segments')
        return max(s.base for s in segments)

    def to_borehole(self, extra_fields=None):
        '''read Dinoloket XML file and return Borehole'''
        # extra fields
        extra_fields = extra_fields or {}
        borehole_fields = extra_fields.get('borehole') or None
        segment_fields = extra_fields.get('segments') or None

        # code
        survey = self.root.find('pointSurvey')
        code = survey.find('identification').attrib.get('id')

        # timestamp of borehole
        date = survey.find('borehole/date')
        try:
            year = self.safe_int(date.attrib.get('startYear'))
            month = self.safe_int(date.attrib.get('startMonth'))
            day = self.safe_int(date.attrib.get('startDay'))
            if year and month and day:
                timestamp = datetime.datetime(year, month, day).isoformat()
            elif year and month:
                timestamp = datetime.datetime(year, month, 1).isoformat()
            elif year:
                timestamp = datetime.datetime(year, 1, 1).isoformat()
            else:
                timestamp = None
        except AttributeError:
            timestamp = None
        self.attrs['timestamp'] = timestamp

        # segments as list
        segments = [s for s in self.read_segments(survey, segment_fields)]

        # final depth of borehole in m
        basedepth = survey.find('borehole').attrib.get('baseDepth')
        depth = self.safe_float(basedepth)
        try:
            depth *= 1e-2  # to m
        except TypeError:
            depth = self.depth_from_segments(segments)

        # x,y coordinates
        coordinates = survey.find('surveyLocation/coordinates')
        x = self.safe_float(coordinates.find('coordinateX').text)
        y = self.safe_float(coordinates.find('coordinateY').text)

        # elevation in m
        elevation = survey.find('surfaceElevation/elevation')
        if not elevation is None:
            z = self.safe_float(elevation.attrib.get('levelValue'))
            try:
                z *= 1e-2  # to m
            except TypeError:
                z = None
        else:
            z = None

        return Borehole(code, depth,
            x=x, y=y, z=z,
            segments=segments,
            **self.attrs,
            )
