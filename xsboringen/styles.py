# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from collections import OrderedDict


class SimpleStylesLookup(object):
    def __init__(self, records, default):
        self.records = {}
        self.itemsdict = OrderedDict()
        for record in records:
            key = record.pop('key')
            self.records[key] = record

            label = record.pop('label')
            self.itemsdict[label] = record

        self.default = default

    def __repr__(self):
        return ('{s.__class__.__name__:}()'
            ).format(s=self)

    def items(self):
        for label, item in self.itemsdict.items():
            yield label, item

    def lookup(self, key):
        return self.records.get(key, self.default)


class ObjectStylesLookup(object):
    def __init__(self, records, default):
        self.attrs = set()
        self.records = []
        self.itemsdict = OrderedDict()
        for record in records:
            keys = record.pop('key')
            if not isinstance(keys, list):
                keys = [keys,]
            for key in keys:
                for attr, values in key.items():
                    self.attrs.add(attr)
                    if not isinstance(values, list):
                        key[attr] = [values,]
                self.records.append((key, record))
            self.itemsdict[record['label']] = record
        self.default = default

    def __repr__(self):
        return ('{s.__class__.__name__:}(attrs={s.attrs:}), '
            ).format(s=self)

    def items(self):
        for label, item in self.itemsdict.items():
            yield label, item
        yield self.default['label'], self.default

    @staticmethod
    def sortkey(item):
        key, record = item
        return -len(key), record['label']

    def lookup(self, obj):
        for key, record in sorted(self.records, key=self.sortkey):
            if all(getattr(obj, k, None) in v for k, v in key.items()):
                return record
        return self.default
