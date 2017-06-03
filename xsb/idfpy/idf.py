#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import numpy as np

import logging
import struct

NAMES = '1271,ncol,nrow,xmin,xmax,ymin,ymax,dmin,dmax,nodata,ieq,itb,mfct'
FMT = '3i7f2?cx'
MULTIPLICATION_FACTORS = {
    1: 1e2,
    2: 1e-2,
    3: 1e3,
    4: 1e-3,
    5: 1e3,
    6: 1e-3
    }


class IDF(object):
    def __init__(self, path, mode='rb', header=None):
        self.filepath = path
        self.mode = mode
        self.f = open(path, mode)
        self.closed = False
        if mode == 'rb':
            self.header = self._read_header()
            self.nodatavals = [self.header['nodata']]
            self.pos = self.f.tell()
        elif mode == 'wb':
            self.header = header
            self.pos = self.f.tell()
        else:
            raise ValueError(
                "mode string must be one of 'rb' or 'wb', not {}".format(mode))

    def __repr__(self):
        return 'IDF(path={path:} mode={mode:}, closed={closed:})'.format(
            path=self.filepath,
            mode=self.mode,
            closed=self.closed and 'closed' or 'open',
            )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self.f.close()
        self.closed = True

    def _read_header(self):
        names = NAMES.split(',')
        header = dict(zip(names, struct.unpack(FMT, self.f.read(4*11))))
        header['mfct'] = ord(header['mfct'])
        if not header['ieq']:
            header['dx'], header['dy'] = struct.unpack('2f', self.f.read(4*2))
        if header['itb']:
            header['top'], header['bot'] = struct.unpack('2f',
                self.f.read(4*2))
        if header['ieq']:
            header['dx(col)'] = struct.unpack('2f',
                self.f.read(4*header['ncol']))
            header['dy(row)'] = struct.unpack('2f',
                self.f.read(4*header['nrow']))
        return header

    def _write_header(self):
        values = [header[n] for n in NAMES.split(',')]
        self.f.write(struct.pack(FMT, values))
        # write mfct
        self.f.write(struct.pack('2f', [header['dx'], header['dy']]))

    def read(self, masked=False):
        if self.closed:
            raise IOError('cannot read closed IDF file')

        # read values
        values = np.fromfile(self.f, np.float32,
            self.header['nrow'] * self.header['ncol'])
        self.f.seek(self.pos)

        # reshape values to array shape(nrow, ncol)
        values = values.reshape(self.header['nrow'], self.header['ncol'])

        # apply multiplication factors if present
        if self.header['mfct'] > 0:
            values *= MULTIPLICATION_FACTORS[self.header['mfct']]
        if self.header['mfct'] > 4:
            if self.header['ieq']:
                cellsize = self.header['dx'] * self.header['dy']
                if self.header['mfct'] == 5:
                    values /= cellsize
                elif self.header['mfct'] == 6:
                    values *= cellsize
            else:
                cellsize = np.meshrid(self.header['dx(col)'],
                    self.header['dy(col)'])
                if self.header['mfct'] == 5:
                    values /= cellsize
                elif self.header['mfct'] == 6:
                    values *= cellsize
        if masked:
            return np.ma.masked_values(values, self.nodatavals[0])
        else:
            return values

    def _write_header(self):
        self.f.write(struct.pack('i'*3, self.header['1271'], self.header['ncol'], self.header['nrow']))
        self.f.write(struct.pack('f'*7, self.header['xmin'], self.header['xmax'], self.header['ymin'],
            self.header['ymax'], self.header['dmin'], self.header['dmax'], self.header['nodata']))
        self.f.write(struct.pack('?'*4, self.header['ieq'], self.header['itb'], 0, 0))
        if not self.header['ieq']:
            self.f.write(struct.pack('f' * 2, self.header['dx'], self.header['dy']))
        if self.header['itb']:
            self.f.write(struct.pack('f' * 2, self.header['top'], self.header['bot']))
        if self.header['ieq']:
            raise NotImplementedError('write method ieq=true not implemented')
        # if not self.header['ivf']:
        #     raise notimplementederror('write method vector=true not implemented')

    def write(self, array):
        if self.closed:
            raise IOError('cannot write to closed IDF file')

        # write header
        self._write_header()

        #write values
        flattened = array.flatten()
        self.f.write(struct.pack('f' * len(flattened), *flattened))

    def is_out(self, row, col):
        return ((col < 0) or (col > self.header['ncol']) or
               (row < 0) or (row > self.header['nrow']))

    def sample(self, coords, bounds_warning=True):
        if self.closed:
            raise IOError('cannot read closed IDF file')

        values = self.read()
        for x, y in coords:
            col = int((x - self.header['xmin']) / self.header['dx'])
            row = int((self.header['ymax'] - y) / self.header['dy'])
            if self.is_out(row, col):
                if bounds_warning:
                    logging.warning((
                        'coordinate pair x, y = {x:.3f}, {y:.3f} out of bounds'
                        .format(x=x, y=y)))
                yield (np.nan,)
            else:
                yield (values[row, col],)
