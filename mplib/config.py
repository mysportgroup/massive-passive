#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__version__ = '0.0.1'
__copyright__ = '(c) 2012 by mysportgroup.de'

import os

try:
    import simplejson as json
except ImportError:
    import json

import logging
from glob import iglob
from shlex import split
from UserDict import IterableUserDict


logger = logging.getLogger(__name__)

class ConfigFile(IterableUserDict):
    def __init__(self, path):
        IterableUserDict.__init__(self)
        self.path = os.path.realpath(path)
        self._initialize()

    def _initialize(self):
        logger = logging.getLogger(
            '%s.%s'
            %(self.__module__, self.__class__.__name__)
        )

        logger.debug('Initialized with %r.', self.path)

        with open(self.path, 'r', 1) as fp:
            try:
                config = json.load(fp)
            except Exception as error:
                logger.error(
                    'There where errors during loading content from: %r',
                    self.path
                )
                logger.exception(error)
                raise
            else:
                self._safe_update(config)

    def _safe_update(self, config):
        must_haves = (
            'check_description',
            'interval',
            'servers',
            'command',
            'check_type',
            'check_hostname'
        )

        for must_have in must_haves:
            if not must_have in config:
                raise KeyError(
                    'Config at %r has no key %r.' %(self.path, must_have)
                )

        command = config['command']
        if isinstance(command, str):
            config['command'] = split(command)
        elif not isinstance(command, (list, tuple)):
            raise TypeError('Command must be one of str, list or tuple')

        self.update(config)

    def reload(self):
        self.clear()
        self._initialize()


class ConfigDir(ConfigFile):
    def _initialize(self):
        logger = logging.getLogger(
            '%s.%s'
            %(self.__module__, self.__class__.__name__)
        )
        logger.debug('Initialized with %r.', self.path)
        for enum, config in enumerate(iglob(os.path.join(self.path, '*.cfg')), 1):
            try:
                config = ConfigFile(config)
            except Exception as error:
                logger.error('There where errors while loading %r. Skipping config.', config)
                logger.exception(error)
                continue
            else:
                self.update({enum: config})



if __name__ == '__main__':
    pass

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4