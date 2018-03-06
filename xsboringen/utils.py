#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import glob
import sys
import os


def careful_glob(folder, pattern):
    if not os.path.exists(folder):
        raise ValueError('folder \'{f:}\' does not exist'.format(
            f=folder,
            ))
    return glob.glob(os.path.join(folder, pattern))


def careful_open(filepath, mode):
    return CarefulFileOpener(filepath=filepath, mode=mode)


class CarefulFileOpener(object):
    def __init__(self, filepath, mode):
        self.filepath = filepath
        self.mode = mode
        self.handle = None

    def retry_dialog(self):
        response = None
        while response not in {'r', 'a'}:
            user_input = input(
                'cannot access \'{fp:}\'\n(R)etry, (A)bort?'.format(
                fp=filepath,
                ))
            try:
                response = user_input.strip().lower()[0]
            except IndexError:
                pass
        if response == 'r':
            self.open()
        elif response == 'a':
            sys.exit('aborting')

    def open(self):
        try:
            self.handle = open(self.filepath, self.mode)
            return self.handle
        except PermissionError:
            self.retry_dialog()

    def close(self):
        if self.handle is not None:
            self.handle.close()
        self.handle = None

    def __enter__(self):
        return self.open()

    def __exit__(self, type, value, traceback):
        self.close()



