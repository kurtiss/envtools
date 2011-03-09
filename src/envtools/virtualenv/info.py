#!/usr/bin/env python
# encoding: utf-8
"""
info.py

Created by Kurtiss Hare on 2011-03-08.
Copyright (c) 2011 Medium Entertainment, Inc. All rights reserved.
"""

import os
import subprocess

__all__ = ['VirtualEnvInfo']


def cachedprop(undecorated):
    private_name = "_{0}".format(undecorated.__name__)
    @property
    def decorated(self):
        if not hasattr(self, private_name):
            setattr(self, private_name, undecorated(self))
        return getattr(self, private_name)
    return decorated


class VirtualEnvInfo(object):
    @classmethod
    def from_env(cls, *args, **kwargs):
        virtual_env = os.getenv('VIRTUAL_ENV')

        if not virtual_env:
            raise RuntimeError("There is no virtualenv activated.")

        return cls(virtual_env, *args, **kwargs)

    def __init__(self, path, workfile = None):
        if not path:
            raise ValueError("'path' cannot be empty.")

        self.path = path
        self._user_workfile = workfile

    @cachedprop
    def workon_home(self):
        return os.path.dirname(self.path)
    
    @cachedprop
    def python_path(self):
        return os.path.join(self.path, "bin/python")
    
    @cachedprop
    def python_version(self):
        process = subprocess.Popen(
            [self.python_path, "-c", """import sys; print ".".join(str(p) for p in sys.version_info[:2])"""],
            stdout = subprocess.PIPE
        )
        out, err = process.communicate()
        return out.strip()
    
    @cachedprop
    def site_packages_dir(self):
        return os.path.join(self.path, "lib/python{0}/site-packages".format(self.python_version))
        
    @cachedprop
    def default_workfile(self):
        return os.path.join(self.path, ".envtools/work")
    
    @property
    def workfile(self):
        if not hasattr(self, '_workfile'):
            if self._user_workfile:
                self._workfile = self._user_workfile
            else:
                self._workfile = self.default_workfile
        return self._workfile
    
    def validate(self):
        if not os.path.isdir(self.workon_home):
            raise RuntimeError("Cannot locate WORKON_HOME directory at {0}.".format(self.workon_home))

        if not os.path.exists(self.python_path):
            raise RuntimeError("Cannot locate python executable at {0}.".format(self.python_path))
        
        if not self.python_version:
            raise RuntimeError("Couldn't determine python version.")
            
        if not os.path.exists(self.workfile):
            os.makedirs(os.path.dirname(self.workfile))
            with open(self.workfile, "a") as f:
                os.utime(self.workfile, None)