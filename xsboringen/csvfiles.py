#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.borehole import Borehole, Segment

from collections import namedtuple
from itertools import groupby
from pathlib import Path
import logging
import glob
import csv
import os

log = logging.getLogger(os.path.basename(__file__))

def boreholes_from_csv(folder,
        fieldnames=None, extra_fields=None,
        delimiter=',', decimal='.'
        ):
    csvfiles = glob.glob(os.path.join(folder, '*.csv'))
    for csvfile in csvfiles:
        csv_ = CSVBoreholeFile(csvfile,
            delimiter=delimiter,
            decimal=decimal,
            )
        for borehole in csv_.to_boreholes(fieldnames, extra_fields):
            if borehole is not None:
                yield borehole


class CSVFile(object):
    # format field
    _format = None

    def __init__(self, csvfile, delimiter=',', decimal='.',
            ):
        self.file = Path(csvfile)
        self.attrs = {
            'source': str(self.file),
            'format': self._format,
            }

        self.delimiter = delimiter
        self.decimal = decimal


class CSVBoreholeFile(CSVFile):
    _format = 'CSV Borehole'
    FieldNames = namedtuple('FieldNames',
        (
            'code', 'depth', 'x', 'y', 'z',
            'top', 'base', 'lithology', 'sandmedianclass'
            )
        )

    @staticmethod
    def safe_int(s):
        try:
            return int(s)
        except ValueError:
            return None

    @staticmethod
    def safe_float(s, decimal='.'):
        if decimal is not '.':
            s = s.replace(decimal, '.') # will break with thousands separator
        try:
            return float(s)
        except:
            return None

    @classmethod
    def cast(cls, s, dtype, decimal):
        if dtype == 'float':
            return cls.safe_float(s, decimal)
        elif dtype == 'int':
            return cls.safe_int(s)
        else:
            return s

    @classmethod
    def read_segments(cls, rows, decimal, fieldnames, fields=None):
        fields = fields or {}
        top = 0.
        for row in rows:
            base = cls.safe_float(row[fieldnames.base], decimal)
            lithology = row[fieldnames.lithology]
            sandmedianclass = row[fieldnames.sandmedianclass]
            attrs = {}
            for field in fields:
                value = row.get(field['fieldname'])
                if value is not None:
                    attrs[field['name']] = cls.cast(value,
                        dtype=field['dtype'],
                        decimal=decimal,
                        )
            yield Segment(top, base, lithology, sandmedianclass, **attrs)

            # base to next top
            top = base

    @staticmethod
    def depth_from_segments(segments):
        log.debug('calculating depth from segments')
        return max(s.base for s in segments)

    def to_boreholes(self, fieldnames, extra_fields=None):
        fieldnames = self.FieldNames(**fieldnames)
        extra_fields = extra_fields or {}
        borehole_fields = extra_fields.get('borehole') or None
        segment_fields = extra_fields.get('segments') or None

        log.debug('reading {s.file.name:}'.format(s=self))
        with open(self.file, 'r') as f:
            reader = csv.DictReader(f, delimiter=self.delimiter)
            bycode = lambda r: r[fieldnames.code]
            for code, rows in groupby(reader, key=bycode):
                if code in {None, ''}:
                    continue

                # materialize rows
                rows = [r for r in rows]

                # code
                code = str(rows[0][fieldnames.code])

                # segments as list
                segments = [
                    s for s in self.read_segments(rows,
                        decimal=self.decimal,
                        fieldnames=fieldnames,
                        fields=segment_fields,
                        )
                    ]

                # depth
                if fieldnames.depth in rows[0]:
                    depth = self.safe_float(rows[0][fieldnames.depth],
                        self.decimal)
                else:
                    depth = self.depth_from_segments(segments)

                # x, y, z
                x = self.safe_float(rows[0][fieldnames.x], self.decimal)
                y = self.safe_float(rows[0][fieldnames.y], self.decimal)
                z = self.safe_float(rows[0][fieldnames.z], self.decimal)

                # extra fields
                if borehole_fields is not None:
                    for field in borehole_fields.items():
                        value = rows[0].get(field['fieldname'])
                        if value is not None:
                            self.attrs[field['name']] = self.cast(value,
                                dtype=field['dtype'],
                                decimal=self.decimal,
                                )

                yield Borehole(code, depth,
                    x=x, y=y, z=z,
                    segments=segments,
                    **self.attrs,
                    )

def boreholes_to_csv(boreholes, csvfile, extra_fields=None):
    log.info('writing to {f:}'.format(f=os.path.basename(csvfile)))
    extra_fields = extra_fields or {}
    borehole_fields = (
        Borehole.fieldnames + (extra_fields.get('borehole') or ())
        )
    segment_fields = (
        Segment.fieldnames + (extra_fields.get('segments') or ())
        )
    with open(csvfile, 'w') as f:
        writer = csv.DictWriter(f,
            fieldnames=borehole_fields + segment_fields,
            lineterminator='\n',
            extrasaction='ignore',
            )
        writer.writeheader()
        for borehole in boreholes:
            for segment in borehole:
                row = borehole.as_dict(borehole_fields)
                row.update(segment.as_dict(segment_fields))
                writer.writerow(row)
