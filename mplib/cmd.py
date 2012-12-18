#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3'
__version__ = '0.0.1'
__copyright__ = '(c) 2012 by mysportgroup.de'

import logging
import subprocess
from Queue import Full

logger = logging.getLogger(__name__)

def passive_check_cmd(check_data, queue, stdout=subprocess.PIPE, stderr=subprocess.PIPE):

    command = check_data.get('command')
    shell = check_data.get('shell', False)
    env = check_data.get('env', None)
    cwd = check_data.get('cwd', '/')
    close_fds = check_data.get('close_fds', True)

    cmd = subprocess.Popen(
        command,
        stdout=stdout,
        stderr=stderr,
        close_fds=close_fds,
        env=env,
        cwd=cwd,
        shell=shell,
    )

    stdout, stderr = cmd.communicate()

    logger.debug('Command %r returned with %s. stdout was: %r, stderr was: %r', command, cmd.returncode, stdout, stderr)

    result = {
        'returncode': cmd.returncode,
        'stdout': stdout,
        'stderr': stderr,
    }

    check_data['check_result'] = result
    queue.put(check_data)
    return check_data

def send_nsca(check_data):
    for host_name, host_ip in check_data.get('servers').iteritems():
        #print "sending to: ", host_ip
        cmd = subprocess.Popen(
            ['/usr/sbin/send_nsca', '-H', host_ip],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            env=None,
            cwd='/',
            close_fds=True,
        )

        stdout, stderr = cmd.communicate(input=check_data['check_result'].get('stdout'))
        logger.debug(
            'Send nsca data for %r returned with %s. stdout was: %r, stderr was: %r',
            check_data['check_result'],
            cmd.returncode,
            stdout,
            stderr
        )


if __name__ == '__main__':
    pass

