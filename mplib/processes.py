#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'

import os
import sys
import multiprocessing
import threading
from cmd import passive_check_cmd, send_nsca
from time import sleep
from Queue import Empty

import logging

logger = logging.getLogger(__name__)

class PoolBarer(threading.Thread):
    def __init__(self, queue, stop_event):
        super(PoolBarer, self).__init__()
        self.name = self.__class__.__name__ + self.name
        self.queue = queue
        self.stop_event = stop_event
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__module__, self.name)
        )

    def run(self):
        while not self.stop_event.is_set():
            self.handle_pools()
        else:
            # safely join the pool at the end again
            self.handle_pools()

    def handle_pools(self):
        while True:
            try:
                pool = self.queue.get(0.1)
            except Empty:
                break
            else:
                #self.queue.task_done()
                pool.close()
                pool.join()
                self.logger.debug('Closed and joined Pool %r', pool)
        return True

class PassiveChecksWorkerPool(threading.Thread):
    def __init__(self, period, passive_checks, out_queue, stop_event):
        super(PassiveChecksWorkerPool, self).__init__()
        self.name = self.__class__.__name__ + self.name
        self.period = period
        self.passive_checks = passive_checks
        self.out_queue = out_queue
        #self.pool_queue = pool_queue
        self.stop_event = stop_event
        self.workers = len(self.passive_checks)
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__module__, self.name)
        )

        self.pool = multiprocessing.Pool(self.workers)

    def run(self):
        while not self.stop_event.is_set():
            #self.logger.debug('Creating new Pool ...')
            #pool = multiprocessing.Pool(self.workers)
            #self.logger.debug('Pool %r created.', pool)
            for check in self.passive_checks:
                #self.logger.debug('Adding %r to pool %r.', check, pool)
                self.pool.apply_async(passive_check_cmd, [check, self.out_queue])
                #self.logger.debug('Put pool %r to the queue %r for the PoolBarer.', pool, self.pool_queue)
                #self.pool_queue.put(pool)
            self.logger.debug('Sleeping %s seconds ...', self.period)
            sleep(self.period)

class SendNscaWorkerPool(threading.Thread):
    def __init__(self, workers, queue, stop_event):
        super(SendNscaWorkerPool, self).__init__()
        self.name = self.__class__.__name__ +  self.name
        self.workers = workers
        self.queue = queue
        self.stop_event = stop_event
        self.pool = multiprocessing.Pool(self.workers)
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__module__, self.name)
        )


    def run(self):
        while not self.stop_event.is_set():
            try:
                check_result = self.queue.get(timeout=0.1)
            except Empty:
                continue
            else:
                self.logger.debug('Adding check_result %r to pool %r.', check_result, self.pool)
                self.pool.apply_async(send_nsca, [check_result])


if __name__ == '__main__':
    pass




    # vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4