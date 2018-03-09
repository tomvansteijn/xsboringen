#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

# 3rd party
import numpy as np

# stdlib
from itertools import tee
import logging

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

class Consolidator(object):
    ''' Functional class for consolidating boreholes by texture and depth'''
    def __init__(self, depth, step, textures):
        self.depth = depth
        self.step = step

        textures.append(config.OTHER)
        self.textures = textures

        # constants (can be changed after instance creation)
        self.dstr = '{:.2f}'

    def _thickness_in_range(self, segment, upper, lower):
        '''get segment thickness within range (upper, lower)'''
        # Segment is within the range (upper, lower)
        if (segment.top >= upper) and (segment.base <= lower):
            return segment.thickness

        # Segment top is within range (upper, lower), base is below lower
        elif (segment.top >= upper) and (segment.top < lower) and (
            segment.base > lower):
            return lower - segment.top

        # Segment top is above upper, base is within range (upper, lower)
        elif (segment.top < upper) and (segment.base > upper) and (
            segment.base <= lower):
            return segment.base - upper

        # Segment top is above upper, base is below lower
        elif (segment.top < upper) and (segment.base > lower):
            return lower - upper
        else:
            return 0.0

    def _get_rows(self):
        '''get results rows filled with zeros'''
        return {self.dstr.format(d): {tx: 0.0 for tx in self.textures} for d in
        np.arange(self.step, self.depth + self.step, self.step)}

    def _select(self, segment):
        '''select segment for processing'''
        return segment.top <= self.depth

    def _get_subrange(self, segment):
        '''get sub range with defined step from segment top, bottom'''
        start = np.floor(segment.top / self.step) * self.step
        if segment.base > self.depth:
            end = np.ceil(self.depth / self.step) * self.step
        else:
            end = np.ceil(segment.base / self.step) * self.step
        return np.arange(start, end + self.step, self.step)

    def _get_medianclass(self, median):
        '''get median class using bins'''
        for (lower, upper), medianclass in config.BINS:
            if (median >= lower) and (median < upper):
                return medianclass

    def _update_lithology(self, rows, segment, upper, lower):
        '''add segment thickness within (upper, lower) to rows'''
        thickness = self._thickness_in_range(segment, upper, lower)
        if segment.lithology in self.textures:
            rows[self.dstr.format(lower)][segment.lithology] += thickness
        else:
            rows[self.dstr.format(lower)][config.OTHER] += thickness

    def _update_sandmedianclass(self, rows, segment, upper, lower):
        '''add segment thickness within (upper, lower) if has sandmedianclass'''
        logging.debug('median class: {}'.format(segment.sandmedianclass))
        if not segment.sandmedianclass and segment.sandmedian:
            segment.sandmedianclass = self._get_medianclass(segment.sandmedian)
            logging.debug('median: {:.1f} >> {}'.format(
                segment.sandmedian, segment.sandmedianclass))
        if segment.sandmedianclass in self.textures:
            thickness = self._thickness_in_range(segment, upper, lower)
            rows[self.dstr.format(lower)][segment.sandmedianclass] += thickness

    def consolidate(self, borehole):
        '''iterate over borehole segments and consolidate'''
        # get empty rows
        rows = self._get_rows()

        # loop over segments
        for segment in borehole:
            if self._select(segment):
                logging.debug('segment {}'.format(segment))

                # update lithology in rows
                for upper, lower in pairwise(self._get_subrange(segment)):
                    logging.debug('in range {:.2f} - {:.2f}'.format(
                        upper, lower))
                    self._update_lithology(rows, segment, upper, lower)
                    self._update_sandmedianclass(rows, segment, upper, lower)

        # convert row keys back to float for proper sorting and return
        return sorted([(float(k), v) for k, v in list(rows.items())])
