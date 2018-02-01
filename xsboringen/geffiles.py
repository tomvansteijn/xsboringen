#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.borehole import Borehole, Segment
from xsboringen.cpt import CPT

from collections import defaultdict, namedtuple
from enum import Enum
from pathlib import Path
import logging
import glob
import os

log = logging.getLogger(os.path.basename(__file__))


def boreholes_from_gef(folder, fieldnames=None):
    geffiles = glob.glob(os.path.join(folder, '*.gef'))
    for geffile in geffiles:
        gef = GefBoreholeFile(geffile, fieldnames)
        borehole = gef.to_borehole()
        if borehole is not None:
            yield borehole


def cpts_from_gef(folder, column_names=None, fieldnames=None):
    geffiles = glob.glob(os.path.join(folder, '*.gef'))
    for geffile in geffiles:
        gef = GefCPTFile(geffile, fieldnames)
        cpt = gef.to_cpt(column_names)
        if cpt is not None:
            yield cpt


class GefFile(object):
    # GEF field names
    FieldNames = namedtuple('FieldNames',
    ['columnsep','recordsep', 'code', 'xy', 'z'])

    # GEF default field names
    _defaultfieldnames = {
        'columnsep': 'COLUMNSEPARATOR',
        'recordsep': 'RECORDSEPARATOR',
        'code': 'TESTID',
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
    class _defaultmeasurementvars(Enum):
        depth = 16

    def __init__(self, geffile, fieldnames=None, measurementvars=None):
        self.file = Path(geffile)
        self.attrs = {
            'source': str(self.file),
            'format': self._format,
            }

        if fieldnames is not None:
            self.fieldnames = self.FieldNames(**fieldnames)
        else:
            self.fieldnames = self.FieldNames(**self._defaultfieldnames)

        if measurementvars is not None:
            self.measurementvars = measurementvars
        else:
            self.measurementvars = self._defaultmeasurementvars

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
    @staticmethod
    def read_segments(lines, columnsep, recordsep):
        for line in lines:
            line = line.rstrip(recordsep)
            attrs = {}
            top, base, *remainder = line.split(columnsep)
            try:
                lithologycolor = remainder[0].replace('\'', '')
            except IndexError:
                lithologycolor = None
            try:
                sandmedianclass = remainder[1].replace('\'', '')
            except IndexError:
                sandmedianclass = None
            try:
                comment = remainder[2].replace('\'', '')
            except IndexError:
                comment = None

            top = float(top)
            base = float(base)
            if lithologycolor not in {'', None}:
                lithology, *color = lithologycolor.split(maxsplit=1)
                attrs['color'] = color
            else:
                lithology = None
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
            depth = self.depth_from_segments(segments)

        # x, y
        _, x, y, *_ = header[self.fieldnames.xy]
        x = float(x)
        y = float(y)

        # z
        if self.fieldnames.z in header:
            _, z, *_ = header[self.fieldnames.z]
            z = float(z)
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

    _defaultcolumn_names = {
        'depth': 'gecorrigeerde diepte',
        'cone_resistance': 'conusweerstand',
        'friction_ratio': 'wrijvingsgetal',
        }

    @classmethod
    def read_verticals(cls, lines, selected_columns, na_values, columnsep, recordsep):
        verticals = defaultdict(list)
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
                    verticals[column].append(value)
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

    def to_cpt(self, column_names=None):
        log.debug('reading {file:}'.format(file=os.path.basename(self.file)))
        column_names = column_names or self._defaultcolumn_names

        with open(self.file) as f:
            lines = (l.rstrip('\n') for l in f if len(l.strip()) > 0)
            header = self.read_header(lines)

            # selected columns
            column_mapping = {v: k for k, v in column_names.items()}
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
        x = float(x)
        y = float(y)

        # z
        if self.fieldnames.z in header:
            _, z, *_ = header[self.fieldnames.z]
            z = float(z)
        else:
            z = None

        return CPT(code, depth,
            x=x, y=y, z=z,
            verticals=verticals,
            **self.attrs,
            )
