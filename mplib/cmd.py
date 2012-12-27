#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__version__ = '0.0.1'
__copyright__ = '(c) 2012 by mysportgroup.de'

import logging
import subprocess
import os

BIN_SEND_NSCA = '/usr/sbin/send_nsca'

logger = logging.getLogger(__name__)

def passive_check_cmd(check_data, queue, stdout=subprocess.PIPE, stderr=subprocess.PIPE):

    command = check_data.get('command')
    shell = check_data.get('shell', False)
    env = check_data.get('env', None)
    cwd = check_data.get('cwd', os.getcwd())
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
    stdout = stdout.rstrip()
    stderr = stderr.rstrip()

    logger.debug('Command %r returned with %s. stdout was: %r, stderr was: %r', command, cmd.returncode, stdout, stderr)

    result = {
        'returncode': cmd.returncode,
        'stdout': stdout,
        'stderr': stderr,
    }

    check_data['check_result'] = result
    queue.put(check_data)
    return check_data

def send_nsca(message, ip, port='5667', timeout='10', delim='\t', config_file='/etc/send_nsca.cfg' ):
    logger.debug(
        'Called with parameters: message => %r, ip => %r, port => %r, timeout => %r, delim => %r, config_file => %r',
        message, ip, port, timeout, delim, config_file
    )

    cmd = subprocess.Popen(
        [BIN_SEND_NSCA, '-H', ip, '-p', port, '-to', timeout, '-d', delim, '-c', config_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        env=None,
        cwd='/',
        close_fds=True,
    )

    stdout, stderr = cmd.communicate(input=message)

    logger.debug(
        'send_nsca returned with %s. message was: %r, stdout was: %r, stderr was: %r',
        cmd.returncode,
        message,
        stdout,
        stderr,
    )

    return cmd.returncode, message, stdout, stderr


if __name__ == '__main__':
    pass

