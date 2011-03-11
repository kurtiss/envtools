#!/usr/bin/env python
# encoding: utf-8
"""
paste.py

Created by Kurtiss Hare on 2011-03-09.
Copyright (c) 2011 Medium Entertainment, Inc. All rights reserved.
"""

from paste.script.create_distro import CreateDistroCommand
from paste.script.templates import Template, var


class CreateProjectCommand(CreateDistroCommand):
    run_args = []

    def __init__(self):
        super(CreateProjectCommand, self).__init__('create')
        self._vars_updated = False

    def run(self, *args):
        return super(CreateProjectCommand, self).run(list(self.run_args) + list(args))
    
    def create_template(self, template, output_dir, vars):
        if not self._vars_updated:
            vars = self.finalize_vars(vars)
            self._vars_updated = True
        return super(CreateProjectCommand, self).create_template(template, output_dir, vars)
    
    def finalize_vars(self, vars):
        return vars


class DynamicVars(object):
    def __init__(self):
        self.getters = []

    def add(self, getter):
        self.getters.append(getter)
        return getter

    def generate(self, template):
        for getter in self.getters:
            class gettervar(var):
                def __init__(self, *args, **kwargs):
                    super(gettervar, self).__init__(getter.__name__, *args, **kwargs)
            template.set_challenge_name(getter.__name__)
            yield getter(template, gettervar)

    def __get__(self, template, owner):
        if not template:
            return self
        return self.generate(template)


class DynamicVarChallenger(object):
    @classmethod
    def wrap(cls, template, cmd):
        if isinstance(cmd.challenge, cls):
            return cmd.challenge
        return cls(template, cmd.challenge)
        
    def __init__(self, template, challenge):
        self.template = template
        self.challenge = challenge
    
    def __call__(self, *args, **kwargs):
        result = self.challenge(*args, **kwargs)
        self.template.set_challenge_result(result)
        return result


class DynamicVarTemplate(Template):
    vars = DynamicVars()

    def __init__(self, *args, **kwargs):
        super(DynamicVarTemplate, self).__init__(*args, **kwargs)
        self.challenge_name = None
        self.checked_vars = None

    def check_vars(self, vars, cmd):
        self.checked_vars = vars.copy()
        cmd.challenge = DynamicVarChallenger.wrap(self, cmd)
        return super(DynamicVarTemplate, self).check_vars(vars, cmd)

    def set_challenge_name(self, name):
        self.challenge_name = name
    
    def set_challenge_result(self, result):
        self.checked_vars[self.challenge_name] = result