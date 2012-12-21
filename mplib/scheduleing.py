#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'
__license__ = 'GPL3+'
__version__ = '0.0.1'


import logging
from mplib.cmd import passive_check_cmd
from apscheduler.scheduler import Scheduler

logger = logging.getLogger(__name__)

class MassivePassiveScheduler(Scheduler):
    def __init__(self, queue):
        super(MassivePassiveScheduler, self).__init__()
        self.queue = queue
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )

    def add_passive_checks(self, checks_config):
        for interval, checks in checks_config.iteritems():
            for check in checks:
                self.logger.info(
                    'Adding check %r with time interval %d.',
                    check.get('name', 'Unnamed'), check.get('interval', 60)
                )
                self.add_interval_job(
                    passive_check_cmd,
                    seconds=interval,
                    args=(check, self.queue)
                )



if __name__ == '__main__':
    pass




# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4