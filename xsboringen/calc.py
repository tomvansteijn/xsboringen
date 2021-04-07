#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from collections import namedtuple
from math import exp
import re


class LithologyRule(object):
    def test(qc, rf):
        raise NotImplementedError('not implemented in base class')


class ExpLithologyRule(LithologyRule):
    _keys = 'left', 'right', 'a', 'b'

    Limit = namedtuple('Limit', _keys)
    def __init__(self, lithology, limits):
        self.lithology = lithology
        self.limits = [self.Limit(**l) for l in limits]

    def __repr__(self):
        return ('{s.__class__.__name__:}(lithology={s.lithology:})').format(
            s=self,
            )

    def test(self, rf, qc):
        for limit in self.limits:
            if (rf > limit.left) and (rf <= limit.right) and qc!=None:
                    return qc > limit.a*exp(limit.b*rf)
        return False

class LithologyClassifier(object):
    def __init__(self, table, ruletype='exponential'):
        self.default = table['default']
        self.ruletype = ruletype

        if ruletype == 'exponential':
            self.rules = [
                ExpLithologyRule(**r) for r in reversed(table['rules'])
                ]
        else:
            raise ValueError('ruletype \'{}\' not supported'.format(ruletype))

    def __repr__(self):
        return ('{s.__class__.__name__:}(ruletype={s.ruletype:})').format(
            s=self,
            )

    def classify(self, rf, qc):
        lithology = self.default
        if not ((rf is None) or (rf < 0.)):  # when rf is nodata
            for rule in self.rules:
                if rule.test(rf, qc):
                    lithology = rule.lithology
        return lithology


class SandmedianClassifier(object):
    Bin = namedtuple('Bin', ['lower', 'upper', 'medianclass'])
    def __init__(self, bins):
        self.bins = [self.Bin(**b) for b in bins]

    def classify(self, median):
        '''get median class using bins'''
        for bin_ in self.bins:
            if (median >= bin_.lower) and (median < bin_.upper):
                return bin_.medianclass


class AdmixClassifier(object):
    def __init__(self, fieldnames):
        self.fieldnames = fieldnames

    def classify(self, lithology_admix):
        attrs = {}
        if lithology_admix is None:
            return attrs
        match = re.match('[A-Z]+', lithology_admix)
        if match is not None:
            attrs['lithology'] = match.group(0)
        admixes = re.findall('[a-z]+?\d?', lithology_admix)
        for admix in admixes:
            key = admix[0].lower()
            admix = admix.upper()
            if len(admix) == 1:
                admix += 'X'
            attrs[self.fieldnames.get(key, key)] = admix.upper()
        return attrs

