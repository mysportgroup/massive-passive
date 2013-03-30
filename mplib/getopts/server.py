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

    parser.add_option(
        '--allowed-client-cert-dir',
        default='/etc/massive-passive/allowed-client-cert.d',
        help=(
            'Only clients with valid certificates in this dir are allowed to ' +
            'send results. Just put the client certs into this dir to authorize them. ' +
            'Default: %default'
        )
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
                msg='No command file found at %s\n' %(
                    options.command_file or ' or '.join(options.command_file_defaults)
                )
            )
        #else:
    #    parser.exit(
    #        status=2,
    #        msg=(
    #            '\nERROR: You must set the path to the nagios/icinga external command file.\n\n%s\n'
    #            %(parser.format_help(),)
    #        )
    #    )

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

    if not options.allowed_client_cert_dir:
        parser.exit(
            status=2,
            msg=(
                '\nERROR: You must set the path to the allowed-client-cert-dir.\n\n%s\n'
                %(parser.format_help(),)
            )
        )
    else:
        if not os.path.exists(options.allowed_client_cert_dir):
            parser.exit(
                status=2,
                msg='No such Directory: %s\n' %(options.allowed_client_cert_dir)
            )
        if not os.path.isdir(options.allowed_client_cert_dir):
            parser.exit(
                status=2,
                msg='This is not a directory: %r\n' %(options.allowed_client_cert_dir)
            )

    return options, args

def get_server_description():
    return (
        'massive-passive is a client/server toolset for scheduling passive nagios/icinga ' +
        'checks. This is the server programm which receives the check results and write ' +
        'them into the nagios/icinga external command file.'
    )


if __name__ == '__main__':
    pass


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4