# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

class SimpleStylesLookup(object):
    def __init__(self, records, default):
        self.mapping = {}
        self.items = []
        for record in records:
            key = record.pop('key')
            label = record.pop('label')
            self.mapping[key] = record
            self.items.append((label, record))
        self.default = default

    def __repr__(self):
        return ('{s.__class__.__name__:}(), '
            ).format(s=self)

    def lookup(self, key):
        return self.mapping.get(key, self.default)


class ObjectStylesLookup(object):
    def __init__(self, attrs, records, default):
        self.attrs = attrs
        self.mapping = {}
        self.items = []
        for record in records:
            key = tuple(record.pop('key'))
            label = record.pop('label')
            self.mapping[key] = record
            self.items.append((label, record))
        self.default = default

    def __repr__(self):
        return ('{s.__class__.__name__:}(attrs={s.attrs:}), '
            ).format(s=self)

    def lookup(self, obj):
        key = tuple(getattr(obj, a, None) for a in self.attrs)
        while key not in self.mapping and len(key) > 0:
            key = key[:-1]
        return self.mapping.get(key, self.default)
