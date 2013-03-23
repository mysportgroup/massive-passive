#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__copyright__ = '(c) 2013 by mysportgroup.de'

import os
import sys
import logging
import pyinotify


logger = logging.getLogger(__name__)

class ProcessEvent(pyinotify.ProcessEvent):
    def my_init(self, **kwargs):
        self.logger = logging.getLogger(
            '%s.%s' %(
                self.__class__.__module__,
                self.__class__.__name__
            )
        )

        self.logger.debug('Initialized with this kwargs: %r', kwargs)

    def process_IN_MODIFY(self, event):
        if not event.name.endswith('.cfg'):
            # silently ignore everything which ends not with '.cfg'
            return None
        print "in modify: %r" %(event,)
        pass

    def process_IN_CLOSE_WRITE(self, event):
        print "in close write: %r" %(event,)
        pass

    def process_IN_DELETE(self, event):
        print "in delete: %r" %(event,)
        pass


class WatchManager(pyinotify.WatchManager):
    pass

class ThreadedNotifier(pyinotify.ThreadedNotifier):
    pass


## Do the same thing than stats.py but with a ThreadedNotifier's
## instance.
## This example illustrates the use of this class but the recommanded
## implementation is whom of stats.py

#class Identity(pyinotify.ProcessEvent):
#    def process_default(self, event):
#        # Does nothing, just to demonstrate how stuffs could be done
#        # after having processed statistics.
#        print 'Does nothing.'

## Thread #1
#wm1 = pyinotify.WatchManager()
#s1 = pyinotify.Stats() # Stats is a subclass of ProcessEvent
#notifier1 = pyinotify.ThreadedNotifier(wm1, default_proc_fun=Identity(s1))
#notifier1.start()
#wm1.add_watch('/tmp/', pyinotify.ALL_EVENTS, rec=True, auto_add=True)

## Thread #2
#wm2 = pyinotify.WatchManager()
#s2 = pyinotify.Stats() # Stats is a subclass of ProcessEvent
#notifier2 = pyinotify.ThreadedNotifier(wm2, default_proc_fun=Identity(s2))
#notifier2.start()
#wm2.add_watch('/var/log/', pyinotify.ALL_EVENTS, rec=False, auto_add=False)

#while True:
#    try:
#        print "Thread 1", repr(s1)
#        print s1
#        print "Thread 2", repr(s2)
#        print s2
#        print
#        time.sleep(5)
#    except KeyboardInterrupt:
#        notifier1.stop()
#        notifier2.stop()
#        break
#    except:
#        notifier1.stop()
#        notifier2.stop()
#        raise

if __name__ == '__main__':
    import time
    watch_manager = WatchManager()
    notifier = ThreadedNotifier(watch_manager, default_proc_fun=ProcessEvent())
    notifier.start()
    watch_manager.add_watch('/tmp/', pyinotify.ALL_EVENTS, rec=False, auto_add=True)
    while True:
        time.sleep(0.1)





    # vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4