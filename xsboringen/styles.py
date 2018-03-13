# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from collections import OrderedDict


class SimpleStylesLookup(object):
    def __init__(self, records=None, default=None):
        records = records or []
        self.records = {}
        self.itemsdict = OrderedDict()
        for i, record in enumerate(records):
            key = record.pop('key')
            label = record.get('label') or 'item_{i:d}'.format(i=i + 1)
            self.add(key, label, record)

        self.default = default or {}
        self.default['label'] = self.default.get('label') or 'item_default'

    def __repr__(self):
        return ('{s.__class__.__name__:}()'
            ).format(s=self)

    def __len__(self):
        return len(self.itemsdict)

    def add(self, key, label, record):
        self.records[key] = record
        self.itemsdict[label] = record

    def items(self):
        for label, item in self.itemsdict.items():
            yield label, item

    def lookup(self, key):
        return self.records.get(key, self.default)


class SegmentStylesLookup(object):
    def __init__(self, records=None, default=None):
        records = records or []
        self.attrs = set()
        self.records = []
        self.itemsdict = OrderedDict()
        for i, record in enumerate(records):
            keys = record.pop('key')
            label = record.get('label') or 'item_{i:d}'.format(i=i + 1)
            if not isinstance(keys, list):
                keys = [keys,]
            for key in keys:
                for attr, values in key.items():
                    self.attrs.add(attr)
                    if not isinstance(values, list):
                        key[attr] = [values,]
                self.records.append((key, record))
            self.itemsdict[label] = record
        self.default = default or {}
        self.default['label'] = self.default.get('label') or 'item_default'

    def __repr__(self):
        return ('{s.__class__.__name__:}(attrs={s.attrs:}), '
            ).format(s=self)

    def __len__(self):
        return len(self.itemsdict)

    def items(self):
        for label, item in self.itemsdict.items():
            yield label, item
        yield self.default['label'], self.default

    @staticmethod
    def sortkey(item):
        key, record = item
        return -len(key)

    def lookup(self, segment):
        for key, record in sorted(self.records, key=self.sortkey):
            if all(getattr(segment, k, None) in v for k, v in key.items()):
                return record
        return self.default
