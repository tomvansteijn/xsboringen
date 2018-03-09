#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsboringen.calc import SandmedianClassifier, AdmixClassifier, LithologyClassifier
from xsboringen.csvfiles import boreholes_to_csv
from xsboringen.datasources import boreholes_from_sources

import logging
import os

log = logging.getLogger(os.path.basename(__file__))


def write_csv(**kwargs):
    # args
    datasources = kwargs['datasources']
    result = kwargs['result']
    config = kwargs['config']

    # read boreholes and CPT's from data folders
    admixclassifier = AdmixClassifier(
        config['admix_fieldnames']
        )
    borehole_sources = datasources.get('boreholes') or []
    boreholes = boreholes_from_sources(borehole_sources, admixclassifier)

    # translate CPT to lithology if needed
    if result.get('translate_cpt', False):
        table = config['cpt_classification']
        lithologyclassifier = LithologyClassifier(table)
        boreholes = (
            b.to_lithology(lithologyclassifier, admixclassifier)
            for b in boreholes
            )

    # classify sandmedian if needed
    if result.get('classify_sandmedian', False):
        bins = config['sandmedianbins']
        sandmedianclassifier = SandmedianClassifier(bins)
        boreholes = (
            b.update_sandmedianclass(sandmedianclassifier) for b in boreholes
            )

    # simplify if needed
    if result.get('simplify', False):
        min_thickness = result.get('min_thickness')
        simplify_by = result.get('simplify_by') or config['simplify_by']
        if not isinstance(simplify_by, list):
            simplify_by = [simplify_by,]
        by = lambda s: {a: getattr(s, a) for a in simplify_by}
        boreholes = (
            b.simplified(min_thickness=min_thickness, by=by)
            for b in boreholes
            )

    # write output to csv
    extra_fields = result.get('extra_fields') or {}
    extra_fields = {k: tuple(v) for k, v in extra_fields.items()}
    boreholes_to_csv(boreholes, result['csvfile'],
        extra_fields=extra_fields,
        )

