#!/usr/bin/env python
# encoding: utf-8
"""
merge.py

Created by Kurtiss Hare on 2011-03-09.
Copyright (c) 2011 Medium Entertainment, Inc. All rights reserved.
"""

import optparse
import sys

from envtools.virtualenv import VirtualEnvInfo

__all__ = ["merge_to_virtualenv"]


def merge_to_virtualenv():
    parser = optparse.OptionParser("Usage: %prog PATH")
    opts, args = parser.parse_args()
    code = 0

    try:
        try:
            path = args[0]
        except IndexError:
            raise RuntimeError("PATH must be specified.")

        virtualenv = VirtualEnvInfo.from_env()
        virtualenv.validate()

        with open(virtualenv.path_extensions, "a+") as f:
            f.seek(0)
            contents = [l for l in f.read().splitlines() if l]

        for line in contents:
            if line == path:
                break
        else:
            contents.append(path)
            with open(virtualenv.path_extensions, "w") as f:
                f.write("\n".join(contents))
    except Exception, e:
        parser.error(e)
        code = 1

    sys.exit(code)