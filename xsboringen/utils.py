#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from pathlib import Path
import glob
import sys
import os


def careful_glob(folder, pattern):
    baseparts = []
    for part in folder.parts:
        if part == '*':
            break
        baseparts.append(part)

    basefolder = Path(*baseparts)
    if not basefolder.exists():
        raise ValueError('folder \'{f:}\' does not exist'.format(
            f=folder,
            ))
    return glob.glob(str(folder / pattern))


def careful_open(filepath, mode):
    return CarefulFileOpener(filepath=filepath, mode=mode)


class CarefulFileOpener(object):
    def __init__(self, filepath, mode):
        self.filepath = Path(filepath)
        self.mode = mode
        self.handle = None

    def __repr__(self):
        return ('{s.__class__.__name__:}(file=\'{s.filepath.name:}\', '
                'mode=\'{s.mode:}\')').format(s=self)

    def retry_dialog(self):
        response = None
        while response not in {'r', 'a'}:
            user_input = input(
                'cannot access \'{fp.name:}\'\n(R)etry, (A)bort?'.format(
                fp=self.filepath,
                ))
            try:
                response = user_input.strip().lower()[0]
            except IndexError:
                pass
        if response == 'r':
            return self.open()
        elif response == 'a':
            sys.exit('aborting')

    def open(self):
        try:
            return open(self.filepath, self.mode)
        except PermissionError:
            return self.retry_dialog()

    def close(self):
        if self.handle is not None:
            self.handle.close()

    def __enter__(self):
        self.handle = self.open()
        return self.handle

    def __exit__(self, type, value, traceback):
        self.close()
        self.handle = None



