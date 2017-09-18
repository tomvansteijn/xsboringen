# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from collections import namedtuple


class StylesLookup(object):
    def __init__(self, attrs, records, default):
        self.attrs = attrs
        self.records = records
        self.default = default

    def __repr__(self):
        return ('{s.__class__.__name__:}(key_attrs={s.key_attrs:}), '
            ).format(s=self)

    def lookup(self, obj, default=None):
        key_values = []
        for attr in self.attrs:
            key_value = getattr(obj, attr, None)
            if key_value is not None:
                key_values.append(key_value)

        key = tuple(key_values)
        while key not in self.records:
            key = key[:-1]
            if not len(key) > 0:
                break

        return self.records.get(key, self.default)
