#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'
__license__ = 'GPL3+'
__version__ = '0.0.1'

import optparse
import logging

logger = logging.getLogger(__name__)

def getopt(usage=None, description=None, version=None, epilog=None):

    parser = optparse.OptionParser(
        usage=usage,
        description=description,
        version=version,
        epilog=epilog
    )

    parser.add_option(
        '--foreground',
        '-f',
        default=False,
        action='store_true',
        help='Do not run in Background. Default: %default'
    )

    parser.add_option(
        '--loglevel',
        '-l',
        choices=['notset', 'NOTSET', 'debug', 'DEBUG', 'info', 'INFO', 'warning', 'WARNING', 'error', 'ERROR'],
        default='INFO',
        help='The loglevel to use. Default: %default'
    )

    parser.add_option(
        '--confdir',
        default='/etc/massive-passive/checks.d',
        help='The path to the passive check configurations directory. Default: %default'
    )

    parser.add_option(
        '--conffile',
        default='/etc/massive-passive/massive-passive.cfg',
        help='The path to the massive_passive config file itself. Default: %default'
    )

    parser.add_option(
        '--pidfile',
        default='/tmp/massive-passive.pid',
        help='The path to the pidfile (if running in Background). Default: %default'
    )

    parser.add_option(
        '--batch-mode',
        default=False,
        action='store_true',
        help='Use batch mode for sending passive check results? Default: %default'
    )

    parser.add_option(
        '--batch-wait-time',
        default=2,
        type='int',
        help='Set the max wait time before sending check results in batch mode. Default: %default',


    )

    options, args = parser.parse_args()

    options.loglevel = getattr(logging, options.loglevel.upper(), logging.INFO)

    return options, args

def get_description():
    return 'massive_passive is a tool for scheduling passive nagios/icinga checks.'

def get_gpl3_text():
    return '''author: Robin Wittler <r.wittler@mysportgroup.de>

Copyright (C) 2012 by mysportgroup.de

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

if __name__ == '__main__':
    pass




# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4