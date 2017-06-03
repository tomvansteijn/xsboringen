# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from .idf import IDF

def open(idfile, mode='rb', header=None):
    return IDF(idfile, mode=mode, header=header)
