#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'

from mplib.config import ConfigDir, ConfigFile
import multiprocessing
from mplib.processes import PassiveChecksWorkerPool
from mplib.processes import SendNscaWorkerPool
from time import sleep
from time import time
import logging
import signal
import threading
import sys

logger = logging.getLogger(__name__)

BASE_FORMAT_SYSLOG = (
    '%(name)s.%(funcName)s[PID: %(process)d | lineno: %(lineno)d] ' +
    '%(levelname)s: %(message)s'
)

BASE_FORMAT_STDOUT = '%(asctime)s ' + BASE_FORMAT_SYSLOG



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format=BASE_FORMAT_STDOUT)
    passive_configs = ConfigDir('./checks.d')
    m = multiprocessing.Manager()
    send_queue = m.Queue()

    stopevent = multiprocessing.Event()
    thread_pool = list()

    send_nsca_pool = SendNscaWorkerPool(2, send_queue, stopevent)
    thread_pool.append(send_nsca_pool)

    for prio, checks in passive_configs.iteritems():
        worker = PassiveChecksWorkerPool(prio, checks, send_queue, stopevent)
        worker.start()
        thread_pool.append(worker)
    send_nsca_pool.start()

    def shutdown(signum, sigframe):
        stopevent.set()
        for thread in thread_pool:
            logger.debug('Joining thread %r ...', thread.name)
            thread.join()
            logger.debug('Joined thread %r.', thread.name)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)

    while not stopevent.is_set():
        sleep(0.1)






# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4