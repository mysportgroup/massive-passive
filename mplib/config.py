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

from glob import iglob
from UserDict import IterableUserDict

class ConfigFile(IterableUserDict):
    def __init__(self, path):
        IterableUserDict.__init__(self)
        self.path = os.path.abspath(path)

    def _initialize(self):
        with open(self.path, 'r', 1) as fp:
            self.update(json.load(fp))

    def reload(self):
        self.clear()
        self._initialize()

class PassiveCheckConfigFile(ConfigFile):
    pass

class ConfigDir(IterableUserDict):
    def __init__(self, path):
        IterableUserDict.__init__(self)
        self.path = os.path.abspath(path)

    def _initialize(self):
        for config in iglob(os.path.join(self.path, '*.cfg')):
            config = PassiveCheckConfigFile(config)
            when = self.setdefault(config['time'], list())
            when.append(config)

    def reload(self):
        self.clear()
        self._initialize()

if __name__ == '__main__':
    pass