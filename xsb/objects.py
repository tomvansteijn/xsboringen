# borehole, cpt, well


class Segment(object):
    def __init__(self, top, base, fields):
        self.top = top
        self.base = base
        self.fields = fields

    @property
    def thickness(self):
        return self.base - self.top


class Point(object):
    self
