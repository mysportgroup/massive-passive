#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__copyright__ = '(c) 2013 by mysportgroup.de'

import os
import pwd
import grp
import optparse
import logging

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
        '--logfile',
        default='/tmp/massive-passive-client.log',
        help='The path to the logfile. Default: %default'
    )

    parser.add_option(
        '--silent',
        default=False,
        action='store_true',
        help='Do not log to stdout. Default: %default'
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
        '--act-as-sender',
        action='store_true',
        default=False,
        help='Act only as a sender. Take input from stdin and send it to server(s). Default: %default'
    )

    parser.add_option(
        '--server',
        default=None,
        help=(
            'The address of one or more massive-passive-servers (comma separated). ' +
            'This option is only valid with the --act-as-sender option. Default: %default'
        )
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

    if options.act_as_sender is True:
        if options.server is None:
            parser.exit(
                status=2,
                msg=(
                    'The --act-as-sender option needs also the --server option set.\n\n%s\n'
                    %(parser.format_help(),)
                )
            )
        else:
            options.server = [server.lstrip(' ').rstrip(' ') for server in options.server.split(',')]

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

if __name__ == '__main__':
    pass


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4