#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__copyright__ = '(c) 2013 by mysportgroup.de'

import logging
import pyinotify
from functools import wraps

logger = logging.getLogger(__name__)


class FilenameEndsWithDecorator(object):
    def __init__(self, ending):
        self.ending = ending

    def __call__(self, func):
        @wraps(func)
        def wrapped(*targs, **kwargs):
            if not targs[-1].name.endswith(self.ending):
                return None
            return func(*targs, **kwargs)
        return wrapped

filename_endswith = FilenameEndsWithDecorator

class ProcessEvent(pyinotify.ProcessEvent):
    def my_init(self, callbacks=None):
        self.logger = logging.getLogger(
            '%s.%s' %(
                self.__class__.__module__,
                self.__class__.__name__
            )
        )

        self.callbacks = callbacks

    @filename_endswith('.cfg')
    def process_IN_CLOSE_WRITE(self, event):
        self.logger.debug(
            'Received IN_CLOSE_WRITE event for %r', event.name
        )

        self.call_callback('IN_CLOSE_WRITE', event)

    @filename_endswith('.cfg')
    def process_IN_DELETE(self, event):
        self.logger.debug(
            'Received IN_DELETE event for %r', event.name
        )

        self.call_callback('IN_DELETE', event)

    def call_callback(self, event_type, event):
        callback = self.callbacks.get(event_type, None)

        if callback is None:
            self.logger.debug('No callback found for event_type %r', event_type)
        elif not callable(callback):
            self.logger.debug('Callback %r for event_type %r is not callable.', callback, event_type)
        else:
            return callback(event)

class WatchManager(pyinotify.WatchManager):
    pass

class ThreadedNotifier(pyinotify.ThreadedNotifier):
    pass


if __name__ == '__main__':
    import time
    from log import BASE_FORMAT_STDOUT
    logging.basicConfig(level=logging.DEBUG, format=BASE_FORMAT_STDOUT)

    watch_manager = WatchManager()
    notifier = ThreadedNotifier(watch_manager, default_proc_fun=ProcessEvent())
    notifier.start()
    watch_manager.add_watch('/tmp/watchdir', pyinotify.IN_CLOSE_WRITE|pyinotify.IN_DELETE, rec=False, auto_add=True)
    while True:
        time.sleep(0.1)
        #notifier.stop()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4