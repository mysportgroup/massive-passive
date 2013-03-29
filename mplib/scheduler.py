#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'
__license__ = 'GPL3+'
__version__ = '0.0.4'


import logging
from time import time
from random import randint
from datetime import datetime
from mplib.cmd import passive_check_cmd
from apscheduler.scheduler import Scheduler

logger = logging.getLogger(__name__)


class MassivePassiveScheduler(Scheduler):
    def __init__(self, queue, **kwargs):
        super(MassivePassiveScheduler, self).__init__(**kwargs)
        self.queue = queue
        self.jobs = dict()
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )

    def __del__(self):
        # prevent references to the logger in the root.manager.loggerDict
        # and having memleaks.
        logging.root.manager.loggerDict.pop(
            '%s.%s' %(self.__class__.__module__, self.__class__.__name__)
        )

    def add_passive_checks(self, checks_config, wait_range_start=2, wait_range_end=10):
        for enum, check in checks_config.iteritems():
            self.logger.debug('Processing %d. check %r ...', enum, check)
            interval = check.get('interval', None)

            if isinstance(interval, int):
                self.logger.info(
                    'Adding %d. check %r with time interval %d as an interval based check.',
                    enum, check.path, check.get('interval')
                )

                try:
                    job = self.add_interval_check(
                        check,
                        wait_range_start=wait_range_start,
                        wait_range_end=wait_range_end
                    )
                except Exception as error:
                    self.logger.exception(error)
                    self.logger.error(
                        'There was an error while adding %d. check %r as an interval based check. Error was: %s',
                        enum, check.path, error
                    )
                else:
                    self.jobs.update({check.path: job})

            elif isinstance(interval, dict):
                self.logger.info(
                    'Adding %d. check %r with %r as a cron based check.'
                    %(enum, check.path, ', '.join(('%s=%r' %(k,v) for k,v in interval.iteritems())))
                )
                try:
                    job = self.add_cron_check(check)
                except Exception as error:
                    self.logger.exception(error)
                    self.logger.error(
                        'There was an error while adding %d. check %r as a cron based check. Error was: %s',
                        enum, check.path, error
                    )
                else:
                    self.jobs.update({check.path: job})

            else:
                self.logger.error(
                    '%d. check %r is has no valid interval attribute. Ignoring it.',
                    enum, check.path
                )

    def remove_job(self, job_path):
        job = self.jobs.pop(job_path, None)
        if job is None:
            self.logger.info('Can not remove job %r - no such job found.', job_path)
            return False
        self.logger.info('Removing job %r from scheduler.', job)
        self.unschedule_job(job)

        return True

    def remove_all_jobs(self):
        for job_path, job in self.jobs.iteritems():
            self.unschedule_job(job)
            self.jobs.pop(job_path)

    def add_interval_check(self, check, wait_range_start=2, wait_range_end=10):
        self.schedule_passive_check_initially(
            check,
            wait_range_start=wait_range_start,
            wait_range_end=wait_range_end
        )

        return self.add_interval_job(
            passive_check_cmd,
            seconds=check.get('interval'),
            max_instances=check.get('max_instances', 1),
            misfire_grace_time=check.get('misfire_grace_time', 5),
            args=(check, self.queue)
        )

    def add_cron_check(self, check):

        interval = check.get('interval')
        year = interval.get('year', None)
        month = interval.get('month', None)
        week = interval.get('week', None)
        day_of_week = interval.get('day_of_week', None)
        hour = interval.get('hour', None)
        minute = interval.get('minute', None)
        second = interval.get('second', None)
        start_date = interval.get('start_date', None)
        args = (check, self.queue)

        return self.add_cron_job(
            passive_check_cmd,
            year=year,
            month=month,
            week=week,
            day_of_week=day_of_week,
            hour=hour,
            minute=minute,
            second=second,
            start_date=start_date,
            args=args,
            max_instances=check.get('max_instances', 1),
            misfire_grace_time=check.get('misfire_grace_time', 5),
        )

    def schedule_passive_check_initially(self, check, wait_range_start=2 , wait_range_end=10):
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