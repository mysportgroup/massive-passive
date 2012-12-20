#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'



import threading
import multiprocessing
from Queue import Empty
from cmd import send_nsca


import logging

logger = logging.getLogger(__name__)


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