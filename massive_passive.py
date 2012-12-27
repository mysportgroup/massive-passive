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
from threading import Event
from mplib import getopts
from mplib.config import ConfigDir
from mplib.daemon import daemonize
from Queue import Queue
from logging.handlers import SysLogHandler
from mplib.threads import SendNscaWorker
from mplib.scheduler import MassivePassiveScheduler


BASE_FORMAT_SYSLOG = (
    '%(name)s.%(funcName)s[PID: %(process)d | lineno: %(lineno)d] ' +
    '%(levelname)s: %(message)s'
)

BASE_FORMAT_STDOUT = '%(asctime)s ' + BASE_FORMAT_SYSLOG


class Main(object):
    def __init__(self, options, send_worker, scheduler, stop_event):
        super(Main, self).__init__()
        self.logger = logging.getLogger(
            '%s.%s' %(
                self.__class__.__module__,
                self.__class__.__name__
            )
        )
        self.options = options
        self.send_worker = send_worker
        self.scheduler = scheduler
        self.stop_event = stop_event
        self.thread_list = list()

    def run(self):
        if self.options.foreground is False:
            self.daemonize()
        self.logger.info('Startup!')
        self.start_threads()
        while not self.stop_event.is_set():
            sleep(0.1)

    def start(self):
        self.run()

    def start_threads(self):
        self.logger.debug('Calling send_worker thread start ...')
        self.send_worker.start()
        self.logger.debug('send_worker thread start called.')
        self.logger.debug('Getting passive check configs ...')
        configs = self.get_check_configs()
        self.scheduler.add_passive_checks(configs)
        self.logger.debug('Calling scheduler start ...')
        self.scheduler.start()
        self.logger.debug('Scheduler start called.')

    def join_threads(self):
        self.logger.debug('Calling scheduler shutdown ...')
        self.scheduler.shutdown()
        self.logger.debug('Scheduler shutdown done.')
        self.logger.debug('Calling send_worker thread join ...')
        self.send_worker.join()
        self.logger.debug('send_worker joined.')

    def daemonize(self):
        daemonize(self.options.pidfile, os.getcwd())

    def get_check_configs(self):
        configs = ConfigDir(self.options.confdir)
        self.logger.debug('Get this from confdir %r: %r', self.options.confdir, configs)
        return configs

    def config_reload(self, signum, sigframe):
        self.logger.info('Received Signal %s ... reloading config now ...', signum)
        self.join_threads()
        self.logger.debug('Getting passive check configs ...')
        configs = self.get_check_configs()
        self.scheduler.add_passive_checks(configs)
        self.start_threads()
        self.logger.info('Config reload done.')


    def shutdown(self, signum, sigframe):
        self.logger.info('Received Signal %s.', signum)
        self.logger.info('Going down now ...')
        self.stop_event.set()
        self.logger.debug('Stopevent set.')
        self.join_threads()

        if self.options.foreground is False:
            self.logger.debug('Removing pidfile at %r', self.options.pidfile)
            try:
                os.unlink(self.options.pidfile)
            except OSError as error:
                self.logger.exception(error)
        self.logger.info('Exiting now!')

if __name__ == '__main__':
    options, args = getopts.getopt(
        version='%prog ' + __version__,
        description=getopts.get_description(),
        epilog=getopts.get_gpl3_text()
    )

    logging.basicConfig(level=options.loglevel, format=BASE_FORMAT_STDOUT)
    root_logger = logging.getLogger('')
    root_logger.setLevel(options.loglevel)
    syslog_logger = SysLogHandler('/dev/log', facility=SysLogHandler.LOG_CRON)
    syslog_logger.setLevel(options.loglevel)
    syslog_formatter = logging.Formatter(BASE_FORMAT_SYSLOG)
    syslog_logger.setFormatter(syslog_formatter)
    root_logger.addHandler(syslog_logger)
    send_queue = Queue()
    stop_event = Event()
    send_nsca_worker = SendNscaWorker(send_queue, stop_event, max_wait=5)
    scheduler = MassivePassiveScheduler(send_queue)
    main = Main(options, send_nsca_worker, scheduler, stop_event)
    signal.signal(signal.SIGTERM, main.shutdown)
    signal.signal(signal.SIGINT, main.shutdown)
    signal.signal(signal.SIGHUP, main.config_reload)
    main.start()
    sys.exit(0)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4