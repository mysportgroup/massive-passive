#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'
__license__ = 'GPL3+'
__version__ = '0.1.0'

import os
import pwd
import grp
import optparse
import logging
from IPy import IP

logger = logging.getLogger(__name__)

def server_getopt(usage=None, description=None, version=None, epilog=None):
    parser = optparse.OptionParser(
        usage=usage,
        description=description,
        version=version,
        epilog=epilog
    )

    parser.add_option(
        '--listen',
        default='0.0.0.0',
        help=(
            'The ip to listen on. At this moment it is only possible to ' +
            'listen at ipv4 or ipv6 - not both at the same time. This limitation ' +
            'will go away in one of the next releases. Default: %default'
        )
    )

    parser.add_option(
        '--port',
        default=5678,
        type='int',
        help='The port to listen on. Default: %default'
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

    # removed this option - follows later
    #parser.add_option(
    #    '--conffile',
    #    default='/etc/massive-passive-client/massive-passive-client.cfg',
    #    help='The path to the massive_passive config file itself. Default: %default'
    #)

    parser.add_option(
        '--pidfile',
        default='/tmp/massive-passive-server.pid',
        help='The path to the pidfile (if running in Background). Default: %default'
    )

    parser.add_option(
        '-u',
        '--user',
        default=pwd.getpwuid(os.getuid()).pw_name,
        help='The username who should execute this process. Default: %default'
    )

    parser.add_option(
        '-g',
        '--group',
        default=grp.getgrgid(os.getgid()).gr_name,
        help='The groupname this process runs at. Default: %default'
    )

    parser.add_option(
        '--logfile',
        default='/tmp/massive-passive-server.log',
        help='The path to the logfile. Default: %default'
    )

    parser.add_option(
        '--command-file',
        #default='/var/lib/icinga/rw/icinga.cmd'
        help=(
            'The path to the nagios/icinga external command file. ' +
            'If not set, it defaults to one of /var/lib/icinga/rw/icinga.cmd or ' +
            '/var/lib/nagios/rw/nagios.cmd - depending which of them exists.'
        )
    )

    parser.add_option(
        '--ssl-ca-cert',
        default='/etc/massive-passive/massive-passive-ssl-ca.cert',
        help='The path to the ssl ca cert. Default: %default'
    )

    parser.add_option(
        '--ssl-key',
        default='/etc/massive-passive/massive-passive-server-ssl.key',
        help='The path to the server ssl key file. Default: %default'
    )

    parser.add_option(
        '--ssl-cert',
        default='/etc/massive-passive/massive-passive-server-ssl.cert',
        help='The path to the server ssl cert file. Default: %default'
    )

    options, args = parser.parse_args()

    options.command_file_defaults = ('/var/lib/icinga/rw/icinga.cmd', '/var/lib/nagios/rw/nagios.cmd')
    options.loglevel = getattr(logging, options.loglevel.upper(), logging.INFO)
    options.user = pwd.getpwnam(options.user).pw_uid
    options.group = grp.getgrnam(options.group).gr_gid

    if not options.listen:
        parser.exit(
            status=2,
            msg=(
                '\nERROR: You must provide a valid ip address to listen on.\n\n%s\n'
                %(parser.format_help(),)
            )
        )
    else:
        try:
            IP(options.listen)
        except Exception:
            parser.exit(
                status=2,
                msg=(
                    '\nERROR: %r is not a valid IP Address.\n\n'
                    %(options.listen,)
                )
            )

    if not options.port:
        parser.exit(
            status=2,
            msg=(
                '\nERROR: You must provide a valid port to listen on.\n\n%s\n'
                %(parser.format_help,)
            )
        )
    else:
        if not options.port in xrange(1, 65536):
            parser.exit(
                status=2,
                msg=(
                    '\nERROR: Port %r is not in range 1-65535.\n\n'
                    %(options.port,)
                )
            )

    if not options.command_file:
        for path in options.command_file_defaults:
            if os.path.exists(path):
                options.command_file = path
                break
        else:
            parser.exit(
                status=2,
                msg=(
                    '\nERROR: You must set the path to the nagios/icinga external command file.\n\n%s\n'
                    %(parser.format_help(),)
                )
            )
    else:
        if not os.path.exists(options.command_file):
            parser.exit(
                status=2,
                msg='No such File: %s\n' %(options.command_file)
        )

    if not options.ssl_ca_cert:
        parser.exit(
            status=2,
            msg=(
                '\nERROR: You must set the path to the ssl ca cert.\n\n%s\n'
                %(parser.format_help(),)
            )
        )
    else:
        if not os.path.exists(options.ssl_ca_cert):
            parser.exit(
                status=2,
                msg='No such File: %s\n' %(options.ssl_ca_cert)
            )


    if not options.ssl_key:
        parser.exit(
            status=2,
            msg=(
                '\nERROR: You must set the path to the server ssl key file.\n\n%s\n'
                %(parser.format_help(),)
            )
        )
    else:
        if not os.path.exists(options.ssl_key):
            parser.exit(
                status=2,
                msg='No such File: %s\n' %(options.ssl_key)
            )

    if not options.ssl_cert:
        parser.exit(
            status=2,
            msg=(
                '\nERROR: You must set the path to the server ssl cert file.\n\n%s\n'
                %(parser.format_help(),)
            )
        )
    else:
        if not os.path.exists(options.ssl_cert):
            parser.exit(
                status=2,
                msg='No such File: %s\n' %(options.ssl_cert)
            )

    return options, args


def client_getopt(usage=None, description=None, version=None, epilog=None):
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

    # removed this option - follows later
    #parser.add_option(
    #    '--conffile',
    #    default='/etc/massive-passive-client/massive-passive-client.cfg',
    #    help='The path to the massive_passive config file itself. Default: %default'
    #)

    parser.add_option(
        '--pidfile',
        default='/tmp/massive-passive-client.pid',
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

    parser.add_option(
        '--batch-max-items',
        default=100,
        type='int',
        help=(
            'How much items to use in batch mode. ' +
            'A value of 0 means unlimited items. Default: %default'
        )
    )

    parser.add_option(
        '-u',
        '--user',
        default=pwd.getpwuid(os.getuid()).pw_name,
        help='The username who should execute this process. Default: %default'
    )

    parser.add_option(
        '-g',
        '--group',
        default=grp.getgrgid(os.getgid()).gr_name,
        help='The groupname this process runs at. Default: %default'
    )

    parser.add_option(
        '--initial-random-wait-range',
        default=10,
        type='int',
        help=(
            'The seconds to random wait before the scheduler executes the ' +
            'jobs the first time. This only applies when starting or reloading ' +
            'the scheduler. The wait range goes from: 2 to INITIAL_RANDOM_WAIT_RANGE. ' +
            'If set to 0, there is no range and every check will be initially scheduled ' +
            'after 2 seconds (which can produce some load). Default: %default'
        )
    )

    parser.add_option(
        '--logfile',
        default='/tmp/massive-passive-client.log',
        help='The path to the logfile. Default: %default'
    )

    parser.add_option(
        '--ssl-key',
        default='/etc/massive-passive/massive-passive-client-ssl.key',
        help='The path to the client ssl key file. Default: %default'
    )

    parser.add_option(
        '--ssl-cert',
        default='/etc/massive-passive/massive-passive-client-ssl.cert',
        help='The path to the client ssl cert file. Default: %default'
    )

    parser.add_option(
        '--ssl-ca-cert',
        default='/etc/massive-passive/massive-passive-ssl-ca.cert',
        help='The path to the ssl ca cert file. Default: %default'
    )

    options, args = parser.parse_args()

    options.loglevel = getattr(logging, options.loglevel.upper(), logging.INFO)
    options.user = pwd.getpwnam(options.user).pw_uid
    options.group = grp.getgrnam(options.group).gr_gid

    if not options.ssl_key:
        parser.exit(
            status=2,
            msg=(
                '\nERROR: You must set the path to the client ssl key file.\n\n%s\n'
                %(parser.format_help(),)
                )
        )
    else:
        if not os.path.exists(options.ssl_key):
            parser.exit(
                status=2,
                msg='No such File: %s\n' %(options.ssl_key)
            )

    if not options.ssl_cert:
        parser.exit(
            status=2,
            msg=(
                '\nERROR: You must set the path to the client ssl cert file.\n\n%s\n'
                %(parser.format_help(),)
                )
        )
    else:
        if not os.path.exists(options.ssl_cert):
            parser.exit(
                status=2,
                msg='No such File: %s\n' %(options.ssl_cert)
            )

    if not options.ssl_ca_cert:
        parser.exit(
            status=2,
            msg=(
                '\nERROR: You must set the path to the ssl ca cert file.\n\n%s\n'
                %(parser.format_help(),)
                )
        )
    else:
        if not os.path.exists(options.ssl_ca_cert):
            parser.exit(
                status=2,
                msg='No such File: %s\n' %(options.ssl_ca_cert)
            )

    return options, args

def get_client_description():
    return (
        'massive-passive is a client/server toolset for scheduling passive nagios/icinga ' +
        'checks. This is the client programm which schedules the checks and sends the ' +
        'results to the massive-passive-server'
    )

def get_server_description():
    return (
        'massive-passive is a client/server toolset for scheduling passive nagios/icinga ' +
        'checks. This is the server programm which receives the check results and write ' +
        'them into the nagios/icinga external command file.'
        )

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