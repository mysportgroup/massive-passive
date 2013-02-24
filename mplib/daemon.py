#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__version__ = '0.0.1'
__copyright__ = '(c) 2012 by mysportgroup.de'

import os
import sys

def daemonize(cwd='/'):

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        msg = "fork #1 failed: (%d) %s\n" % (e.errno, e.strerror)
        sys.stderr.write(msg)
        sys.exit(1)

    os.chdir(cwd)
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


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4