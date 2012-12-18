#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3'
__version__ = '0.0.1'
__copyright__ = '(c) 2012 by mysportgroup.de'

import os
import sys

def daemonize():

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        msg = "fork #1 failed: (%d) %s\n" % (e.errno, e.strerror)
        sys.stderr.write(msg)
        sys.exit(1)

    os.chdir('/')
    os.umask(0)
    os.setsid()

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        msg = "fork #2 failed: (%d) %s\n" % (e.errno, e.strerror)
        sys.stderr.write(msg)
        sys.exit(1)


    pid = os.getpid()
    pidfile_fd = os.open(
        '/tmp/massive_passive.pid',
        os.O_CREAT | os.O_EXCL | os.O_RDWR,
        0640
    )
    pidfile = os.fdopen(pidfile_fd, 'w+')
    pidfile.write('%s\n' %(pid,))
    pidfile.flush()
    os.close(pidfile_fd)

    stdin = open('/dev/null', 'r')
    stdout = open('/dev/null', 'a+')
    stderr = open('/dev/null', 'a+')
    sys.stdout.flush()
    sys.stderr.flush()

    os.dup2(stdin.fileno(), sys.stdin.fileno())
    os.dup2(stdout.fileno(), sys.stdout.fileno())
    os.dup2(stderr.fileno(), sys.stderr.fileno())


if __name__ == '__main__':
    pass

