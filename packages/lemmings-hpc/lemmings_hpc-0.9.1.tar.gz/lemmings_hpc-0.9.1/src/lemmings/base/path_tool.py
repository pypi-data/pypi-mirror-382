#!/usr/bin/env python
# pylint: disable=no-value-for-parameter
# -*- coding: utf-8 -*-
"""path_tools.py

Concentrate path and file manipulaiton tools.  
Created Nov 2016 by COOP team
"""

from __future__ import absolute_import

import os
import shutil
import errno
from lemmings.lemmingslogging import lemlog

from os.path import (
    abspath,
    basename,
    isabs,
    isfile,
    normpath,
    realpath,
    isdir,
    join,
    relpath,
    samefile,
)

__all__ = ["PathTools"]


class PathTools:
    """Concentrate path manipulation tools"""

    def __init__(self, base_dir=None):
        self.base_dir = os.getcwd() if base_dir is None else base_dir

    def abspath(self, *args):
        """Get path as clean absolute

        If args starts with absolute path, just abspath it.  Else, consider
        from self.base_dir, then abspath.  Note: os.path.abspath also performs
        normpath, which "cleans" any ../ and such.
        """
        interpret_path_from = (
            join(*args) if isabs(args[0]) else join(self.base_dir, *args)
        )
        return normpath(realpath(abspath(interpret_path_from)))

    def relpath(self, *args):
        """Get path as clean relative from base_dir"""
        return "./" + normpath(relpath(realpath(self.abspath(*args)), self.base_dir))

    def _file_checks(self, src, dest):
        """Generic checks before moving or copying src to dest

        - If dest is a folder, src file name is kept. Otherwise, given file
          name is used.
        - If source and dest are the same file, no error is raised but a
          warning is printed.

        Return go_code (True: continue. False: skip) and destination
        """
        dest = self.abspath(dest)
        if isdir(dest):
            dest = join(dest, basename(src))

        if isfile(src) and isfile(dest) and samefile(src, dest):
            # shutil.copy doesn't like same files
            lemlog(
                "No copy for the same file: {0} and {1}".format(src, dest),
                level="warning",
            )
            return False, dest

        return True, dest

    def copy_file(self, src, dest):
        """Copy file src to dest"""
        copy_is_ok, dest = self._file_checks(src, dest)
        if copy_is_ok:
            lemlog("Copying {0} to {1}".format(src, dest), level="debug")
            shutil.copy(src, dest)
        return dest

    def copy_dir(self, src, dest):
        """Copy dir src to dest
        - If dest ends with /, src dir is copied in dest dir.  Otherwise, src
        dir is copied *as* dest dir.  This mirrors the `cp` command behavior.
        - If dest is a regular file, raise an error.
        - If source and dest are the same dir, no error is raised but a warning
        is printed.
        """
        if dest[-1] == "/":
            dest = join(dest, basename(src))

        dest = self.abspath(dest)
        if isfile(dest):
            lemlog(
                "Trying to create/populate directory {0}, but it "
                "is already a regular file".format(dest),
                level="warning",
            )
            raise OSError(errno.EEXIST)

        # shutil.copy doesn't like same files
        if isdir(src) and isdir(dest) and samefile(src, dest):
            lemlog(
                "No copy for the same file: {0} and {1}".format(src, dest),
                level="warning",
            )
            return

        if not isdir(dest):
            os.mkdir(dest)

        lemlog("Copying {0} to {1}".format(src, dest), level="warning")
        for path in os.listdir(src):
            if isdir(path):
                self.copy_dir(join(src, path), join(dest, path))
            else:
                self.copy_file(join(src, path), dest)
