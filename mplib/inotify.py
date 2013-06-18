#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__copyright__ = '(c) 2013 by mysportgroup.de'
__version__ = '0.1.0'

import os
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

class ProcessConfigEvents(pyinotify.ProcessEvent):
    def my_init(self, callbacks=None):
        self.logger = logging.getLogger(
            '%s.%s' %(
                self.__class__.__module__,
                self.__class__.__name__
            )
        )

        self.callbacks = callbacks

    @filename_endswith('.cfg')
    def process_default(self, event):
        self.logger.debug(
            'Received %r event for %r', event.maskname, event.pathname
        )

        if event.maskname == 'IN_CREATE' and not os.path.islink(event.pathname):
            # if a link is created in the watched dir, then there will be only
            # a IN_CREATE event. But a regular file, which will be copied, have
            # also a IN_CLOSE_WRITE event - and we wait for that event.
            self.logger.debug(
                'Received %r for regular file %r - ignoring it.',
                event.maskname,
                event.pathname
            )
            return None

        return self.call_callback(event)

    def call_callback(self, event):
        callback = self.callbacks.get(event.maskname, None)
        if callback is None:
            self.logger.debug('No callback found for event_type %r', event.maskname)
        elif not callable(callback):
            self.logger.debug('Callback %r for event_type %r is not callable.', callback, event.maskname)
        else:
            return callback(event)

class ProcessPemEvents(ProcessConfigEvents):
    @filename_endswith('.pem')
    def process_default(self, event):
        self.logger.debug(
            'Received %r event for %r', event.maskname, event.pathname
        )

        if event.maskname == 'IN_CREATE' and not os.path.islink(event.pathname):
            # if a link is created in the watched dir, then there will be only
            # a IN_CREATE event. But a regular file, which will be copied, have
            # also a IN_CLOSE_WRITE event - and we wait for that event.
            self.logger.debug(
                'Received %r for regular file %r - ignoring it.',
                event.maskname,
                event.pathname
            )
            return None

        return self.call_callback(event)


class WatchManager(pyinotify.WatchManager):
    pass

class ThreadedNotifier(pyinotify.ThreadedNotifier):
    pass


if __name__ == '__main__':
    pass

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4