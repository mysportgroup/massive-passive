#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'
__license__ = 'GPL3+'
__version__ = '0.1.0'

import os
import sys
import signal
import logging
from time import sleep
import multiprocessing
from mplib import getopts
from mplib.config import ConfigDir
from mplib.daemon import daemonize
from Queue import Queue as PoolQueue
from logging.handlers import SysLogHandler
from mplib.processes import SendNscaWorkerPool
from mplib.scheduleing import MassivePassiveScheduler


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

    send_nsca_pool.start()
    global scheduler
    scheduler = MassivePassiveScheduler(send_queue)
    scheduler.add_passive_checks(passive_configs)
    scheduler.start()

    def config_reload(signum, sigframe):
        logger.info('Received SIGHUP ... reloading config now ...')
        global scheduler
        scheduler.shutdown()
        scheduler = MassivePassiveScheduler(send_queue)
        passive_configs = ConfigDir(options.confdir)
        scheduler.add_passive_checks(passive_configs)
        scheduler.start()
        logger.info('Config reload done.')


    def shutdown(signum, sigframe):
        logger.info('Received SIGTERM ... going down now ...')
        stopevent.set()
        scheduler.shutdown()
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
    signal.signal(signal.SIGHUP, config_reload)

    while not stopevent.is_set():
        sleep(0.1)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4