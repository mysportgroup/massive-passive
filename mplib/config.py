#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3'
__version__ = '0.0.1'
__copyright__ = '(c) 2012 by mysportgroup.de'

import os

try:
    import simplejson as json
except ImportError:
    import json

import logging
from glob import iglob
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
            self.update(json.load(fp))

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
        for config in iglob(os.path.join(self.path, '*.cfg')):
            config = ConfigFile(config)
            when = self.setdefault(config['interval'], list())
            when.append(config)


if __name__ == '__main__':
    pass