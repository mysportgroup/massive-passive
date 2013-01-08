#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'
__license__ = 'GPL3+'
__version__ = '0.0.4'


from time import time
from Queue import Empty
from Queue import Queue
from cmd import send_nsca
from threading import Thread


import logging

logger = logging.getLogger(__name__)

class WorkerJoiner(Thread):
    def __init__(self, in_queue, stop_event):
        super(WorkerJoiner, self).__init__()
        self.name = self.__class__.__name__ +  self.name
        self.in_queue = in_queue
        self.stop_event = stop_event
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__module__, self.name)
        )

    def run(self):
        while not self.stop_event.is_set():
            try:
                process = self.in_queue.get(True, 0.1)
            except Empty:
                continue
            else:
                self.logger.debug('Joining process %r ...', process)
                process.join()
                self.logger.debug('Joined process %r.', process)


class SendNscaExecutor(Thread):
    def __init__(self, socket, message, path_to_send_nsca):
        super(SendNscaExecutor, self).__init__()
        self.name = self.__class__.__name__ + self.name
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__module__, self.name)
        )

        self.socket = socket
        self.message = message
        self.excetued = False
        self.path_to_send_nsca = path_to_send_nsca

    def run(self):
        self.logger.debug(
            'Executing %r with socket %r and message %r.',
            self.path_to_send_nsca,
            self.socket,
            self.message
        )

        returncode, message, stdout, stderr = send_nsca(
            self.message,
            self.socket,
            path_to_send_nsca=self.path_to_send_nsca
        )

        if returncode:
            self.logger.info(
                'send_nsca job to %r was not successful.', self.socket
            )
        else:
            self.logger.info(
                'send_nsca job to %r was successful.', self.socket
            )

        self.logger.debug(
            'send_nsca to %r returned with %r, stdout was %r, stderr was %r.',
            self.socket,
            returncode,
            stdout,
            stderr
        )
        self.excetued =True


class SendNscaWorker(Thread):
    def __init__(self, in_queue, stop_event, max_wait=1, max_results=10, batch_mode=False, path_to_send_nsca='/usr/sbin/send_nsca'):
        super(SendNscaWorker, self).__init__()
        self.name = self.__class__.__name__ +  self.name
        self.in_queue = in_queue
        self.out_queue = Queue()
        self.stop_event = stop_event
        self.max_wait = max_wait
        self.max_results = max_results
        self.batch_mode = batch_mode
        self.path_to_send_nsca = path_to_send_nsca
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__module__, self.name)
        )
        self.process_joiner = WorkerJoiner(self.out_queue, self.stop_event)
        self.logger.debug('Starting %r thread ...', self.process_joiner.name)
        self.process_joiner.start()
        self.logger.debug('%r thread started.', self.process_joiner.name)


    def run(self):
        while not self.stop_event.is_set():
            results = self._get_from_in_queue()
            workers = self._build_workers(results)
            self._put_into_out_queue(workers)
        else:
            self.logger.debug(
                'Joining %r thread ...', self.process_joiner.name
            )

            self.process_joiner.join()

            self.logger.debug(
                'Joined %r thread.', self.process_joiner.name
            )

            self.logger.debug(
                '%r is alive: %r',
                self.process_joiner.name,
                self.process_joiner.is_alive()
            )

    def _get_from_in_queue(self):
        start_time = time()
        end_time = start_time + self.max_wait
        results = list()

        while not self.stop_event.is_set():
            if self.batch_mode is True:
                if self.max_results and (len(results) >= self.max_results):
                    self.logger.debug('Hitting max_results limit ...')
                    break

                if results and time() > end_time:
                    self.logger.debug('Hitting max_wait limit ...')
                    break

            try:
                results.append(self.in_queue.get(True, 0.1))
            except Empty:
                continue
            else:
                if self.batch_mode is False:
                    break

        return results

    def _put_into_out_queue(self, workers):
        for worker in workers:
            self.out_queue.put(worker)

    def _build_workers(self, results):
        workers = list()


        if self.batch_mode is False:
            self.logger.debug(
                'Sending %s results in single mode.', len(results)
            )
            for result in results:
                for socket in result['servers'].itervalues():
                    socket = socket.split(':', 1)
                    process = SendNscaExecutor(
                        socket,
                        self._format_result(result),
                        self.path_to_send_nsca
                    )
                    process.start()
                    workers.append(process)
        else:
            self.logger.debug(
                'Sending %s results in batch mode.', len(results)
            )
            batch_mapping = dict()
            for result in results:
                for socket in result['servers'].itervalues():
                    string_list = batch_mapping.setdefault(socket, list())
                    string_list.append(self._format_result(result))
            for socket, string_list in batch_mapping.iteritems():
                socket = socket.split(':')
                process = SendNscaExecutor(socket, ''.join(string_list), self.path_to_send_nsca)
                process.start()
                workers.append(process)
        return workers

    def _raw_format_result(self, result):
        return result['check_result']['stdout']

    def _format_result(self, result, delim='\t'):
        check_type = result['check_type']
        check_hostname = result['check_hostname']
        check_returncode = result['check_result']['returncode']
        check_msg = result['check_result']['stdout']

        if check_type == 'host_check':
            #Host Checks Format:
            #<host>\t<return_code>\t<plugin_output>\n
            return '%s%s%s%s%s\n' %(
                check_hostname, delim, check_returncode, delim, check_msg
            )

        if check_type == 'service_check':
            #Service Checks Format:
            #<host>\t<svc_description>\t<return_code>\t<plugin_output>\n
            check_description = result['check_description']
            return '%s%s%s%s%s%s%s\n' %(
                check_hostname,
                delim,
                check_description,
                delim,
                check_returncode,
                delim,
                check_msg
            )


if __name__ == '__main__':
    pass




# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4