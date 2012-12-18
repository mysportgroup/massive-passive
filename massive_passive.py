#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'

from mplib.config import ConfigDir, ConfigFile
import multiprocessing
from mplib.processes import PassiveChecksWorkerPool
from mplib.processes import SendNscaWorkerPool
from mplib.processes import PoolBarer
from time import sleep
from Queue import Queue as PoolQueue
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
    pool_queue = PoolQueue()

    stopevent = multiprocessing.Event()
    thread_list = list()

    send_nsca_pool = SendNscaWorkerPool(2, send_queue, stopevent)
    thread_list.append(send_nsca_pool)




    for prio, checks in passive_configs.iteritems():
        worker = PassiveChecksWorkerPool(prio, checks, send_queue, pool_queue, stopevent)
        worker.start()
        thread_list.append(worker)

    pool_barer = PoolBarer(pool_queue, stopevent)
    pool_barer.daemon = True
    send_nsca_pool.start()
    pool_barer.start()

    def shutdown(signum, sigframe):
        logger.info('Received SIGTERM ... going down now ...')
        stopevent.set()
        logger.debug('Stopevent set.')
        for thread in thread_list:
            logger.debug('Joining thread %r ...', thread.name)
            thread.join()
            logger.debug('Joined thread %r.', thread.name)
        logger.info('Exiting now!')
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)

    while not stopevent.is_set():
        sleep(0.1)



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4