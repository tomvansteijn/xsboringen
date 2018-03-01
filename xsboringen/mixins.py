#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import copy


class AsDictMixin(object):
    '''Mixin for mapping class attributes to dictionary'''
    def as_dict(self, keys=None):
        if keys:
            return {k: getattr(self, k, None) for k in keys}
        else:
            return {k: v for k, v in self.__dict__.items()
                if not k.startswith('__')}


class CopyMixin(object):
    '''Mixin for adding copy method to object'''
    def copy(self, deep=False):
        if deep:
            return copy.deepcopy(self)
        else:
            return copy.copy(self)
