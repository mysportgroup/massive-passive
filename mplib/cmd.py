#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__version__ = '0.0.3'
__copyright__ = '(c) 2012 by mysportgroup.de'

import logging
import subprocess
from uuid import uuid4 as create_job_id

BIN_SEND_NSCA = '/usr/sbin/send_nsca'

logger = logging.getLogger(__name__)

def passive_check_cmd(check_data, queue, stdout=subprocess.PIPE, stderr=subprocess.PIPE):

    check_description = check_data.get('check_description')
    command = check_data.get('command')
    env = check_data.get('env', None)
    cwd = check_data.get('cwd', '/')
    close_fds = check_data.get('close_fds', True)

    logger.info('Executing %r (command is: %r).', check_description, ' '.join(command))

    cmd = subprocess.Popen(
        command,
        stdout=stdout,
        stderr=stderr,
        close_fds=close_fds,
        env=env,
        cwd=cwd,
        shell=False,
    )

    stdout, stderr = cmd.communicate()
    stdout = stdout.rstrip()
    stderr = stderr.rstrip()

    logger.info(
        'Check %r (command %r) returned with %s. stdout was: %r, stderr was: %r',
        check_description, ' '.join(command), cmd.returncode, stdout, stderr
    )

    result = {
        'returncode': cmd.returncode,
        'stdout': stdout,
        'stderr': stderr,
    }

    check_data['check_result'] = result
    queue.put(check_data)
    return check_data

def send_nsca(message, socket, port='5667', timeout='10', delim='\t',
              config_file='/etc/send_nsca.cfg', path_to_send_nsca=BIN_SEND_NSCA):
    jobid = create_job_id()
    logger.debug(
        (
            'Called with parameters: message => %r, socket => %r, '
            'port => %r, timeout => %r, delim => %r, config_file => %r, '
            'path_to_send_nsca => %r, jobid => %s'
        ),
        message, socket, port, timeout, delim, config_file, path_to_send_nsca, jobid
    )

    ip = socket[0]
    if len(socket) > 1:
        port = socket[1]

    logger.info(
        'send_nsca (job_id %s) to %s is running for message: %r', jobid, ':'.join(socket), message
    )

    cmd = subprocess.Popen(
        [path_to_send_nsca, '-H', ip, '-p', port, '-to', timeout, '-d', delim, '-c', config_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        env=None,
        cwd='/',
        close_fds=True,
    )

    stdout, stderr = cmd.communicate(input=message)

    return jobid, cmd.returncode, message, stdout, stderr


if __name__ == '__main__':
    pass

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4