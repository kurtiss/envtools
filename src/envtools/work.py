#!/usr/bin/env python
# encoding: utf-8
"""
addwork.py

Created by Kurtiss Hare on 2011-03-07.
"""

import contextlib
import optparse
import os
import subprocess
import StringIO
import sys
import logging

from envtools.virtualenv import VirtualEnvInfo

__all__ = ['addwork', 'rmwork', 'lswork']


class WorkCommand(object):
    def __init__(self, virtualenv):
        self.virtualenv = virtualenv

    def addwork(self, *incoming):
        if not incoming:
            raise RuntimeError("No projects were specified.")
        
        class ProcessError(RuntimeError):
            pass

        with open(self.virtualenv.workfile, "a+") as f:
            existing = set(f.readlines())
            incoming = set(incoming)
            candidates = incoming - existing

            for project in candidates:
                if project not in existing:
                    try:
                        try:
                            process = subprocess.Popen(
                                [self.virtualenv.python_path, "setup.py", "develop"],
                                cwd = "{0}/{1}".format(self.virtualenv.workon_home, project),
                                stderr = subprocess.PIPE,
                            )

                            out, err = process.communicate()
                            if process.returncode > 0:
                                raise ProcessError(err)
                        except OSError, e:
                            raise ProcessError(e)
                    except ProcessError, e:
                        raise RuntimeError("Couldn't addwork for '{0}':\n{1}".format(project, e))

                    f.write("{0}\n".format(project))
                    existing.add(project)
                else:
                    logging.warn("Project '{0}' was not added, since it's already being worked upon.".format(project))

    def rmwork(self, *incoming):
        if not incoming:
            raise RuntimeError("No projects were specified.")

        incoming = set(incoming)
        
        with open(self.virtualenv.workfile, "r") as f:
            existing = set(f.read().splitlines())

        target_remaining = existing - incoming
        target_remove = existing - target_remaining
        ignore = incoming - target_remove
        
        for project in ignore:
            logging.warn("Project '{0}' was not removed, since it's not being worked upon.".format(project))


        unlinked = dict()

        try:
            for project in target_remove:
                link = os.path.join(self.virtualenv.site_packages_dir, "{0}.egg-link".format(project))
            
                with open(link, "r") as linkfile:
                    path = linkfile.readline().rstrip()

                os.remove(link)

                unlinked[project] = dict(
                    link = link,
                    path = path
                )
        finally:
            remaining = existing - set(unlinked.keys())

            with open(self.virtualenv.workfile, "w") as f:
                f.write("\n".join(remaining))
                
            unlinked_paths = set([entry['path'] for entry in unlinked.values()])
            easy_install_path = os.path.join(self.virtualenv.site_packages_dir, "easy-install.pth")

            with open(easy_install_path, "r") as f:
                easy_install_lines = f.read().splitlines()

            easy_install_lines = [l for l in easy_install_lines if l not in unlinked_paths]

            with open(easy_install_path, "w") as f:
                f.write("\n".join(easy_install_lines))

    def lswork(self):
        with open(self.virtualenv.workfile, "r") as f:
            lines = [l for l in f.read().splitlines() if l]
            sys.stdout.write("\n".join(lines))
            if lines:
                sys.stdout.write("\n")
            sys.stdout.flush()

def addwork():
    parser = create_parser("Usage: %prog PROJECT [PROJECT...]")
    with work_command_runner(parser) as (opts, args, command):
        command.addwork(*args)

def rmwork():
    parser = create_parser("Usage: %prog PROJECT [PROJECT...]")
    with work_command_runner(parser) as (opts, args, command):
        command.rmwork(*args)

def lswork():
    parser = create_parser("Usage: %prog")
    with work_command_runner(parser) as (opts, args, command):
        command.lswork()
    
def create_parser(usage):
    parser = optparse.OptionParser(usage)

    parser.add_option("-w", "--workfile",
        dest = "workfile",
        help = "Path to the file used to manage projects being worked upon."
    )

    return parser

@contextlib.contextmanager
def work_command_runner(parser):
    opts, args = parser.parse_args()
    code = 0

    try:
        virtualenv = VirtualEnvInfo.from_env(workfile = opts.workfile)
        virtualenv.validate()

        yield opts, args, WorkCommand(virtualenv)
    except RuntimeError, e:
        parser.error(e)
        code = 1

    sys.exit(code)