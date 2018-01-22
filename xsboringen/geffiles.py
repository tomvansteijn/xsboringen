#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.borehole import Borehole, Segment
from xsboringen.cpt import CPT

from collections import defaultdict, namedtuple
import logging
import os

log = logging.getLogger(os.path.basename(__file__))


GefFieldNames = namedtuple('FieldNames', ['columnsep', 'recordsep', 'code', 'depth', 'xy', 'z'])


def read_headerline(lines):
    line = next(lines)
    var, value = line.split('=')
    return  (
            var.lstrip('#').strip().lower(),
            value.strip().split(','),
            )


def read_header(lines, repeatedset):
    header = defaultdict(dict)
    var, values = read_headerline(lines)
    while var != 'eoh':
        if var in repeatedset:
            *values, identifier = values
            identifier = identifier.strip()
            if identifier not in header[var]:
                header[var][identifier] = []
            header[var][identifier].append(values)
        else:
            header[var] = values
        var, values = read_headerline(lines)
    return header


def segments_from_gef(lines, separator, recordsep):
    for line in lines:
        line = line.rstrip(recordsep)
        attrs = {}
        top, base, lithology, sandmedianclass, comment, *_ = line.split(separator)
        top = float(top)
        base = float(base)
        lithology = lithology.replace('\'', '')
        sandmedianclass = sandmedianclass.replace('\'', '')
        attrs['comment'] = comment.replace('\'', '')
        yield Segment(top, base, lithology, sandmedianclass, **attrs)


def borehole_from_gef(geffile, fieldnames, repeatedset):
    log.debug('reading {file:}'.format(file=os.path.basename(geffile)))
    attrs = {}
    attrs['source'] = geffile

    with open(geffile) as f:
        lines = (l.rstrip('\n') for l in f if len(l.strip()) > 0)
        header = read_header(lines, repeatedset)

        # column separator
        columnsep, *_ = header[fieldnames.columnsep]

        # record separator (ending)
        recordsep, *_ = header[fieldnames.recordsep]

        # segments
        segments = segments_from_gef([l for l in lines], columnsep, recordsep)

    # code
    code = header[fieldnames.code]

    # depth
    depth, *_ = header['measurementvar'][fieldnames.depth]

    # x, y
    _, x, y, *_ = header[fieldnames.xy]
    x = float(x)
    y = float(y)

    # z
    if fieldnames.z in header:
        _, z, *_ = header[fieldnames.z]
        z = float(z)
    else:
        z = None

    return Borehole(code, depth,
        x=x, y=y, z=z,
        segments=segments,
        **attrs,
        )


# REPEATEDSET = {'columninfo', 'columnvoid', 'measurementtext', 'measurementvars'}
# COLUMN_MAP = {
#         'gecorrigeerde diepte': 'depth',
#         'wrijvingsgetal rf': 'friction_ratio',
#         'conusweerstand qc': 'cone_resistance'}

# COLUMN_MAP = {
#         'diepte': 'depth',
#         'wrijvingsgetal': 'friction_ratio',
#         'conusweerstand': 'cone_resistance'}


# def cpts_from_gef(folder, mapping=None, delimiter=';', nodatavalue=-999):
#     cptfiles = glob.glob(os.path.join(folder, '*.gef'))
#     for cptfile in cptfiles:
#         yield cpt_from_gef(geffile)


# def readmetadataline(f):
#     """read line of metadata from GEF"""
#     line = f.readline().rstrip('\n')
#     key, value = line.split('=', 1)
#     key = key.strip().lower().lstrip('#')
#     value = value.strip()
#     return key, value


# def safe_float(s):
#     try:
#         return float(s)
#     except:
#         return None


# def readdata(f, delimiter=None):
#     """read data lines from GEF"""
#     data = []
#     for line in f:
#         if delimiter is None:
#             data.append([safe_float(v)
#             for v in line.rstrip('\n').split() if v.strip()])
#         else:
#             data.append([safe_float(v)
#             for v in line.rstrip('\n').split(delimiter) if v.strip()])
#     return zip(*data)


# def clean_name(dirty_name):
#     """clean string to column name"""
#     unit, name, *_ = dirty_name.split(',')
#     return name.strip().lower()


# def map_column(name, column_map):
#     """map columns to predefined column names"""
#     try:
#         return next(v for k, v in column_map.items() if k.startswith(name))
#     except StopIteration:
#         return None


# def cpt_from_gef(geffile, nodatavalue=-999, delimiter=' ', column_map=None):
#     """read cpt from GEF file and return as Cpt object"""
#     logging.info('reading {}'.format(os.path.basename(geffile)))
#     with open(geffile) as f:
#         # source file name
#         file = os.path.basename(geffile)

#         # read until end of header and fill metadata dict
#         meta = {}
#         key, value = readmetadataline(f)
#         while not key == 'eoh':
#             if key in REPEATEDSET:
#                 number, value = value.split(',', 1)
#                 key = key + '_' + number
#             meta[key] = value
#             key, value = readmetadataline(f)

#         # code
#         if 'testid' in meta:
#             code = meta['testid']
#         elif 'gefid' in meta:
#             code = meta['gefid']
#         else:
#             code = None

#         # X,Y-coordinates
#         _, x, y, *_ = meta['xyid'].split(',')
#         x = float(x)
#         y = float(y)

#         # Z-value
#         if 'zid' in meta:
#             _, z, *_ = meta['zid'].split(',')
#             z = float(z)
#         else:
#             z = nodatavalue

#         # start date
#         try:
#             startdate = [int(v) for v in meta['startdate'].split(',')]
#         except:
#             startdate = None

#         # start time
#         try:
#             starttime = [int(v) for v in meta['starttime'].split(',')]
#         except:
#             starttime = [0, 0, 0]

#         # start date & time to datetime
#         if startdate is not None:
#             date = datetime.datetime(*startdate, *starttime)
#         else:
#             date = None

#         # get column names
#         column_map = column_map or {}
#         colnum = lambda t: (int(t[0].split('_')[-1]), t[1])
#         columns = [map_column(clean_name(v), column_map)
#             for k, v in sorted(((k, v) for k, v in meta.items()
#             if k.startswith('columninfo')), key=colnum)]

#         # read data if present and return cpt as object
#         logging.debug(
#             'reading {count:d} columns of data from {file:}'.format(
#             count=len(columns), file=geffile))
#         data = readdata(f, delimiter=delimiter)
#         data = {k: c for k, c in zip(columns, data) if k is not None} or None
#     return Borehole(code, depth,
#         x=x, y=y, z=z,
#         segments=segments,
#         **attrs,
#         )


