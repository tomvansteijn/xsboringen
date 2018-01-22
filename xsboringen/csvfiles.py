#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.borehole import Borehole, Segment

from collections import namedtuple
from itertools import groupby
import glob
import csv
import os

log = logging.getLogger(os.path.basename(__file__))

FieldNames = namedtuple('FieldNames', ['code', 'x', 'y', 'z', 'base', 'lithology', 'sandmedianclass'])


def segments_from_csv(rows, fieldnames, extra_fields=None):
    extra_fields = extra_fields or {}
    top = 0.
    for row in rows:
        base = float(row[fieldnames.base])
        lithology = row[fieldnames.lithology]
        sandmedianclass = row[fieldnames.sandmedianclass]
        attrs = {a: row[fn] for a, fn in extra_fields}
        yield Segment(top, base, lithology, sandmedianclass, **attrs)

        # base to next top
        top = base


def borehole_from_csv(csvfile, rows, fieldnames, extra_fields=None):
    '''read CSV file and return Borehole'''
    attrs = {}
    attrs['source'] = csvfile

    rows = [r for r in rows]
    code = rows[0][fieldnames.code]
    depth = float(rows[-1][fieldnames.base])
    x = float(rows[0][fieldnames.x])
    y = float(rows[0][fieldnames.y])
    z = float(rows[0][fieldnames.z])

    # segments as generator
    segments = segments_from_csv(rows, fieldnames, extra_fields)

    return Borehole(code, depth,
        x=x, y=y, z=z,
        segments=segments,
        **attrs,
        )


def boreholes_from_csv(csvfile, fieldnames, extra_fields=None):
    log.debug('reading {file:}'.format(file=os.path.basename(csvfile)))
    with open(csvfile, 'r') as f:
        reader = csv.DictReader(f)
        bycode = lambda r: r[fieldnames.code]
        for code, rows in groupby(reader, key=bycode):
            if code is in {None, ''}:
                continue
            yield borehole_from_csv(csvfile, rows, fieldnames, extra_fields)


def boreholes_to_csv(boreholes, csvfile, attrs=None):
    log.info('writing to {f:}'.format(f=os.path.basename(csvfile)))
    fieldnames = Borehole.fieldnames + Segment.fieldnames + (attrs or [])
    with open(csvfile, 'w') as f:
        writer = csv.DictWriter(f,
            fieldnames=fieldnames,
            lineterminator='\n',
            extrasaction='ignore',
            )
        writer.writeheader()
        for borehole in boreholes:
            for segment in borehole:
                row = borehole.as_dict()
                row.update(segment.as_dict())
                writer.writerow(row)
