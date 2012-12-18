#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'
__version__ = '0.1.0'

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
import os
import sys
from mplib import getopts
from mplib.daemon import daemonize
from logging.handlers import SysLogHandler



BASE_FORMAT_SYSLOG = (
    '%(name)s.%(funcName)s[PID: %(process)d | lineno: %(lineno)d] ' +
    '%(levelname)s: %(message)s'
)

BASE_FORMAT_STDOUT = '%(asctime)s ' + BASE_FORMAT_SYSLOG

if __name__ == '__main__':
    options, args = getopts.getopt(
        version='%prog ' + __version__,
        description=getopts.get_description(),
        epilog=getopts.get_gpl3_text()
    )

    logging.basicConfig(level=options.loglevel, format=BASE_FORMAT_STDOUT)

    if options.foreground is False:
        daemonize(options.pidfile, os.getcwd())


    root_logger = logging.getLogger('')
    root_logger.setLevel(options.loglevel)
    logger = logging.getLogger(sys.argv[0])
    logger.setLevel(options.loglevel)
    syslog_logger = SysLogHandler('/dev/log', facility=SysLogHandler.LOG_CRON)
    syslog_logger.setLevel(options.loglevel)
    syslog_formatter = logging.Formatter(BASE_FORMAT_SYSLOG)
    syslog_logger.setFormatter(syslog_formatter)
    root_logger.addHandler(syslog_logger)

    logger.info('Startup!')

    passive_configs = ConfigDir(options.confdir)
    manager = multiprocessing.Manager()
    send_queue = manager.Queue()
    pool_queue = PoolQueue()

    stopevent = multiprocessing.Event()
    thread_list = list()

    send_nsca_pool = SendNscaWorkerPool(2, send_queue, stopevent)
    thread_list.append(send_nsca_pool)

    for prio, checks in passive_configs.iteritems():
        #worker = PassiveChecksWorkerPool(prio, checks, send_queue, pool_queue, stopevent)
        worker = PassiveChecksWorkerPool(prio, checks, send_queue, stopevent)
        logger.debug('Starting worker %r ...', worker)
        worker.start()
        thread_list.append(worker)

    #pool_barer = PoolBarer(pool_queue, stopevent)
    #pool_barer.daemon = True
    send_nsca_pool.start()
    #pool_barer.start()

    def shutdown(signum, sigframe):
        logger.info('Received SIGTERM ... going down now ...')
        stopevent.set()
        logger.debug('Stopevent set.')
        for thread in thread_list:
            logger.debug('Joining thread %r ...', thread.name)
            thread.join()
            logger.debug('Joined thread %r.', thread.name)
        logger.info('Exiting now!')
        if options.foreground is False:
            try:
                os.unlink(options.pidfile)
            except OSError as error:
                logging.exception(error)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while not stopevent.is_set():
        sleep(0.1)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4