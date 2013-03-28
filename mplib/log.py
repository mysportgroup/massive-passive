#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__copyright__ = '(c) 2013 by mysportgroup.de'

import os
import sys
import logging

logger = logging.getLogger(__name__)

BASE_FORMAT_SYSLOG = (
    '%(name)s.%(funcName)s[%(process)d] ' +
    '%(levelname)s: %(message)s'
)

BASE_FORMAT_STDOUT = '%(asctime)s ' + BASE_FORMAT_SYSLOG

EXTENDED_FORMAT_SYSLOG = (
    '%(name)s.%(funcName)s[PID: %(process)d | lineno: %(lineno)d] ' +
    '%(levelname)s: %(message)s'
)

EXTENDED_FORMAT_STDOUT = '%(asctime)s ' + BASE_FORMAT_SYSLOG


def set_logfile_permissions(path):
    os.chown(path, os.getuid(), os.getgid())
    os.chmod(path, 0660)



if __name__ == '__main__':
    pass


    # vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4