#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from collections import namedtuple


def classify_sandmedian(median, bins):
    '''get median class using bins'''
    for (lower, upper), medianclass in bins:
        if (median >= lower) and (median < upper):
            return medianclass


class ClassificationSegment(object):
    def __init__(self, left, right, lim_f):
        self.left = left
        self.right = right
        self.lim_f = lim_f

    def __contains__(self, x):
        return (x > self.left) and (x <= self.right)

    def limit(self, value):
        return self.lim_f(value)


class ClassificationRule(object):
    def __init__(self, limits, params, ):
        self.segments = []
        for rule in rules:




    def __iter__(self):
        for segment in self.segments:
            yield segment

class Classifier(object):
    def __init__(self, rules, default='O'):
        self.default = default
        self.rules = [ClassificationRule]

    def classify(rf, qc):
        lithology = self.default
        for rule in rules:
            for segment in rule:
                if rf in segment and qc > segment.limit(rf):
                    lithology = rule.lithology
        return lithology


def lithology_from_cur(rf, qc, cur_rules, default_lithology='O'):
    lithology = default_lithology
    if rf < 0.:  # when rf is nodata
        return lithology
    else:
        for rule in rules:
            if (((rf > rule['l1']) and (rf <= rule['l2']) and
                (qc > (rule['a1'] * exp(rule['b1'] * rf)))) or
                ((rf > rule['l2']) and (rf <= rule['l3']) and
                    (qc > (rule['a2'] * exp(rule['b2'] * rf))))):
                lithology = rule['lithology']
        return lithology
