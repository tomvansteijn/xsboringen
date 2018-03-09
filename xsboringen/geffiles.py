#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.borehole import Borehole, Segment, Vertical
from xsboringen.cpt import CPT
from xsboringen import utils

from collections import defaultdict, namedtuple
from pathlib import Path
import textwrap
import logging
import os

log = logging.getLogger(os.path.basename(__file__))


def boreholes_from_gef(folder, classifier=None, fieldnames=None):
    geffiles = utils.careful_glob(folder, '*.gef')
    for geffile in geffiles:
        gef = GefBoreholeFile(geffile, classifier, fieldnames)
        borehole = gef.to_borehole()
        if borehole is not None:
            yield borehole


def cpts_from_gef(folder, datacolumns=None, classifier=None, fieldnames=None):
    geffiles = utils.careful_glob(folder, '*.gef')
    for geffile in geffiles:
        gef = GefCPTFile(geffile, classifier, fieldnames)
        cpt = gef.to_cpt(datacolumns)
        if cpt is not None:
            yield cpt


class GefFile(object):
    # GEF field names
    FieldNames = namedtuple('FieldNames',
    ['columnsep','recordsep', 'code', 'measurementcode', 'xy', 'z'])

    # GEF measurement vars codes
    MeasurementVars = namedtuple('MeasurementVars',
    ['depth', ])

    # GEF default field names
    _defaultfieldnames = {
        'columnsep': 'COLUMNSEPARATOR',
        'recordsep': 'RECORDSEPARATOR',
        'code': 'TESTID',
        'measurementcode': 'MEASUREMENTCODE',
        'xy': 'XYID',
        'z': 'ZID',
        }

    # format field
    _format = None

    # GEF header sections
    ColumnInfo = namedtuple('ColumnInfo',
        ['number', 'unit', 'name', 'quantity_number'])

    ColumnVoid = namedtuple('ColumnVoid',
        ['number', 'value'])

    MeasurementText = namedtuple('MeasurementText',
        ['number', 'value', 'name']
        )

    MeasurementVar = namedtuple('MeasurementVar',
        ['number', 'value', 'unit', 'name']
        )

    SpecimenText = namedtuple('SpecimenText',
        ['number', 'value', 'name']
        )

    SpecimenVar = namedtuple('SpecimenVar',
        ['number', 'value', 'unit', 'name']
        )

    # GEF measurementvar codes
    _defaultmeasurementvars = {
        'depth': 16,
        }

    def __init__(self, geffile,
        classifier=None,
        fieldnames=None,
        measurementvars=None,
        ):
        self.file = Path(geffile)
        self.attrs = {
            'source': str(self.file),
            'format': self._format,
            }
        self.classifier = classifier

        if fieldnames is not None:
            self.fieldnames = self.FieldNames(**fieldnames)
        else:
            self.fieldnames = self.FieldNames(**self._defaultfieldnames)

        if measurementvars is not None:
            self.measurementvars = self.MeasurementVars(**measurementvars)
        else:
            self.measurementvars = self.MeasurementVars(
                **self._defaultmeasurementvars
                )

    @staticmethod
    def safe_int(s):
        try:
            return int(s)
        except ValueError:
            return None

    @staticmethod
    def safe_float(s):
        try:
            return float(s)
        except:
            return None

    @staticmethod
    def read_headerline(lines):
        line = next(lines)
        var, values = line.split('=')
        return  (
                var.lstrip('#').strip(),
                values.strip(),
                )

    @classmethod
    def read_header(cls, lines):
        header = {}
        var, values = cls.read_headerline(lines)
        while var != 'EOH':
            if var == 'COLUMNINFO':
                if var not in header:
                    header[var] = {}
                number, unit, name, quantity_number = values.split(',', 3)
                columninfo = cls.ColumnInfo(
                    cls.safe_int(number),
                    unit.strip(),
                    name.strip(),
                    cls.safe_int(quantity_number),
                    )
                header[var][columninfo.number] = columninfo
            elif var == 'COLUMNVOID':
                if var not in header:
                    header[var] = {}
                number, na_value = values.split(',', 1)
                columnvoid = cls.ColumnVoid(
                    cls.safe_int(number),
                    cls.safe_float(na_value),
                    )
                header[var][columnvoid.number] = columnvoid
            elif var == 'MEASUREMENTTEXT':
                if var not in header:
                    header[var] = {}
                number, value, name = values.split(',', 2)
                measurementtext = cls.MeasurementText(
                    cls.safe_int(number),
                    value.strip(),
                    name.strip(),
                    )
                header[var][measurementtext.number] = measurementtext
            elif var == 'MEASUREMENTVAR':
                if var not in header:
                    header[var] = {}
                number, value, unit, *name = values.split(',', 3)
                if not name:
                    name = ''
                else:
                    name = name[0]
                measurementvar = cls.MeasurementVar(
                    cls.safe_int(number),
                    cls.safe_float(value),
                    unit.strip(),
                    name.strip(),
                    )
                header[var][measurementvar.number] = measurementvar
            elif var == 'SPECIMENTEXT':
                if var not in header:
                    header[var] = {}
                number, value, name = values.split(',', 2)
                specimentext = cls.SpecimenText(
                    cls.safe_int(number),
                    value.strip(),
                    name.strip(),
                    )
                header[var][specimentext.number] = specimentext
            elif var == 'SPECIMENVAR':
                if var not in header:
                    header[var] = {}
                number, value, unit, name = values.split(',', 3)
                specimenvar = cls.SpecimenVar(
                    cls.safe_int(number),
                    cls.safe_float(value),
                    unit.strip(),
                    name.strip(),
                    )
                header[var][specimenvar.number] = specimenvar
            else:
                header[var] = values.split(',')
            var, values = cls.read_headerline(lines)
        return header


class GefBoreholeFile(GefFile):
    _format = 'GEF Borehole'

    @classmethod
    def read_segments(cls, lines, columnsep, recordsep):
        for line in lines:
            line = line.rstrip(recordsep)
            attrs = {}
            top, base, *remainder = line.split(columnsep)
            try:
                lithologycolor = remainder[0].replace('\'', '').strip() or None
            except IndexError:
                lithologycolor = None
            try:
                sandmedianclass = remainder[1].replace('\'', '').strip() or None
            except IndexError:
                sandmedianclass = None
            try:
                comment = remainder[2].replace('\'', '').strip() or None
            except IndexError:
                comment = None

            top = cls.safe_float(top)
            base = cls.safe_float(base)
            if lithologycolor is not None:
                lithology, *color = lithologycolor.split(maxsplit=1)
                attrs['color'] = color
            else:
                lithology = None
            if sandmedianclass is not None:
                sandmedianclass, *_ = sandmedianclass.split(maxsplit=1)
            if comment is not None:
                attrs['comment'] = comment
            yield Segment(top, base, lithology, sandmedianclass, **attrs)

    @staticmethod
    def depth_from_segments(segments):
        log.debug('calculating depth from segments')
        return max(s.base for s in segments)

    def to_borehole(self):
        log.debug('reading {file:}'.format(file=os.path.basename(self.file)))

        with open(self.file) as f:
            lines = (l.rstrip('\n') for l in f if len(l.strip()) > 0)
            header = self.read_header(lines)

            # column separator
            if self.fieldnames.columnsep in header:
                columnsep, *_ = header[self.fieldnames.columnsep]
            else:
                columnsep = None

            # record separator
            if self.fieldnames.recordsep in header:
                recordsep, *_ = header[self.fieldnames.recordsep]
            else:
                recordsep = None

            # segments
            segments = [
                s for s in self.read_segments(lines, columnsep, recordsep)
                ]
            # classify lithology and admix
            if self.classifier is not None:
                for segment in segments:
                    segment.update(self.classifier.classify(segment.lithology))
        # code
        try:
            code = header[self.fieldnames.code][0].strip()

        except KeyError:
            log.warning(
                (
                    'no value for \'{s.fieldnames.code:}\' in {s.file.name:},\n'
                    'skipping this file'
                    ).format(s=self))
            return

        # depth
        try:
            depth = header['MEASUREMENTVAR'][self.measurementvars.depth].value
        except KeyError:
            depth = self.depth_from_segments(segments)

        # x, y
        _, x, y, *_ = header[self.fieldnames.xy]
        x = self.safe_float(x)
        y = self.safe_float(y)

        # z
        if self.fieldnames.z in header:
            _, z, *_ = header[self.fieldnames.z]
            z = self.safe_float(z)
        else:
            z = None

        return Borehole(code, depth,
            x=x, y=y, z=z,
            segments=segments,
            **self.attrs,
            )


class GefCPTFile(GefFile):
    _format = 'GEF CPT'
    Columns = namedtuple('GefCPTColumns',
        ['depth', 'cone_resistance', 'friction_ratio'])

    _defaultdatacolumns = {
        'depth': 'gecorrigeerde diepte',
        'cone_resistance': 'conusweerstand',
        'friction_ratio': 'wrijvingsgetal',
        }

    @classmethod
    def read_verticals(cls, lines, selected_columns, na_values, columnsep, recordsep):
        items = defaultdict(list)
        for line in lines:
            line = line.rstrip(recordsep)
            if columnsep is None:
                valuestrs = [v for v in line.split() if v.strip()]
            else:
                valuestrs = line.split(columnsep)
            for i, valuestr in enumerate(valuestrs):
                column = selected_columns.get(i + 1)
                na_value = na_values.get(i + 1)
                if column is not None:
                    value = cls.safe_float(valuestr)
                    if value == na_value:
                        value = None
                    items[column].append(value)
        try:
            depth = items.pop('depth')
        except KeyError:
            depth = None
        verticals = {}
        for key, values in items.items():
            verticals[key] = Vertical(name=key, depth=depth, values=values)
        return verticals

    @staticmethod
    def depth_from_verticals(verticals):
        log.debug('calculating depth from verticals')
        try:
            return verticals['depth'][-1]
        except KeyError:
            return None
        except IndexError:
            return None

    def to_cpt(self, datacolumns=None):
        log.debug('reading {file:}'.format(file=os.path.basename(self.file)))
        datacolumns = datacolumns or self._defaultdatacolumns

        with open(self.file) as f:
            lines = (l.rstrip('\n') for l in f if len(l.strip()) > 0)
            header = self.read_header(lines)

            # selected columns
            column_mapping = {v: k for k, v in datacolumns.items()}
            selected_columns = {
                i: column_mapping.get(ci.name)
                for i, ci in header['COLUMNINFO'].items()
                }

            # column na values
            na_values = {
                i: cv.value
                for i, cv in header['COLUMNVOID'].items()
                }

            # column separator
            if self.fieldnames.columnsep in header:
                columnsep, *_ = header[self.fieldnames.columnsep]
            else:
                columnsep = None

            # record separator
            if self.fieldnames.recordsep in header:
                recordsep, *_ = header[self.fieldnames.recordsep]
            else:
                recordsep = None

            # verticals
            verticals = self.read_verticals(lines,
                selected_columns,
                na_values,
                columnsep,
                recordsep,
                )

        # code
        try:
            code = header[self.fieldnames.code][0]
        except KeyError:
            log.warning(
                (
                    'no value for \'{s.fieldnames.code:}\' in {s.file.name:},\n'
                    'skipping this file'
                    ).format(s=self))
            return

        # depth
        try:
            depth = header['MEASUREMENTVAR'][self.measurementvars.depth].value
        except KeyError:
            depth = self.depth_from_verticals(verticals)

        # x, y
        _, x, y, *_ = header[self.fieldnames.xy]
        x = self.safe_float(x)
        y = self.safe_float(y)

        # z
        if self.fieldnames.z in header:
            _, z, *_ = header[self.fieldnames.z]
            z = self.safe_float(z)
        else:
            z = None

        return CPT(code, depth,
            x=x, y=y, z=z,
            verticals=verticals,
            **self.attrs,
            )
