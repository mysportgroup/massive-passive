#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'
__license__ = 'GPL3+'
__version__ = '0.0.3'


import logging
from time import time
from random import randint
from datetime import datetime
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
                    check.path, check.get('interval', 60)
                )
                self.add_interval_job(
                    passive_check_cmd,
                    seconds=interval,
                    max_instances=check.get('max_instances', 1),
                    misfire_grace_time=check.get('misfire_grace_time', 2),
                    args=(check, self.queue)
                )
    def schedule_passive_checks_initially(self, checks_config, wait_range_start=2 , wait_range_end=10):
        for checks in checks_config.itervalues():
            for check in checks:
                date = datetime.fromtimestamp(
                    time() + randint(
                        wait_range_start,
                        wait_range_end if wait_range_end else wait_range_start
                    )
                )
                self.logger.info(
                    'Check %r will be initially executed at %s.',
                    check,
                    date
                )
                self.add_date_job(
                    passive_check_cmd,
                    date=date,
                    args=(check, self.queue)
                )


if __name__ == '__main__':
    pass




# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4