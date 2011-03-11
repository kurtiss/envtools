#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Created by Kurtiss Hare on 2011-03-09.
Copyright (c) 2011 Medium Entertainment, Inc. All rights reserved.
"""

import glob
import os
import optparse
import stat
import sys

from datetime import datetime
from envtools.mkskeleton.pasty import CreateProjectCommand, DynamicVarTemplate
from envtools.virtualenv import VirtualEnvInfo


__all__ = ['mkskeleton']


class MkSkeletonCommand(CreateProjectCommand):
    run_args = ["--template", "standard", "--quiet"]
    
    def finalize_vars(self, vars):
        vars.update(dict(
            empty = "",
            now = datetime.now().strftime("%Y-%m-%d"),
            copyright = "\n{0}".format(vars['copyright']) if vars['copyright'] else ""
        ))
        return vars


class StandardProjectTemplate(DynamicVarTemplate):
    summary = 'Standard Project Template'
    vars = DynamicVarTemplate.vars

    def template_dir(self):
        return os.path.join(self.module_dir(), 'templates/standard')

    @vars.add
    def author(self, var):
        return var('e.g. Jeff Beck', 'Anonymous')

    @vars.add
    def author_email(self, var):
        username = self.checked_vars['author'].split(" ")[0].lower()
        return var(None, '{0}@gmail.com'.format(username))

    @vars.add
    def copyright(self, var):
        return var(None,
            'All copyright interest in this code is dedicated to the public domain.'
        )

    @vars.add
    def project_url(self, var):
        username = self.checked_vars['author'].split(" ")[0].lower()
        return var(None,
            'http://www.github.com/{0}/{1}'.format(username, self.checked_vars['project'])
        )


def mkskeleton():
    parser = optparse.OptionParser("Usage: %prog [options] PROJECT")
    opts, args = parser.parse_args()

    try:
        try:
            project_name = args[0]
        except IndexError:
            raise RuntimeError("PROJECT must be specified.")
    
        # invoke paste's creation functionality
        MkSkeletonCommand().run(project_name)
    except Exception, e:
        parser.error(e)
        sys.exit(1)
    
    sys.exit(0)