#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__copyright__ = '(c) 2012 by mysportgroup GmbH'
__license__ = 'GPL3+'
__version__ = '0.1.0'


from time import time
from Queue import Empty
from Queue import Queue
from threading import Thread
from mplib.net.client import PassiveCheckSubmitClient


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
                if process.executed is True:
                    self.logger.debug('Joining process %r ...', process)
                    process.join()
                    self.logger.debug('Joined process %r.', process)
                else:
                    self.in_queue.put(process)


class SendNativeExecutor(Thread):
    def __init__(self, socket, message, ssl_key, ssl_cert, ssl_ca_cert, timeout=3, default_port=5678):
        super(SendNativeExecutor, self).__init__()
        self.name = self.__class__.__name__ + self.name
        self.socket = socket
        self.message = message
        self.executed = False
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        self.ssl_ca_cert = ssl_ca_cert
        self.timeout = timeout
        self.default_port = default_port
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__module__, self.name)
        )

    def run(self):
        self.logger.debug('Starting for socket %r and message %r', self.socket, self.message)
        socket = self.socket.split(':', 1)
        if len(socket) > 1:
            ip = socket[0]
            port = int(socket[1])
        else:
            ip = socket[0]
            port = self.default_port

        self.logger.info('Sending %d messages to %r', len(self.message), self.socket)

        client = PassiveCheckSubmitClient(
            message='\n'.join(self.message) + '\n',
            ip=ip,
            port=port,
            ssl_key=self.ssl_key,
            ssl_cert=self.ssl_cert,
            ssl_ca_cert=self.ssl_ca_cert,
            timeout=self.timeout
        )

        try:
            client.run()
        except Exception as error:
            self.logger.error(
                'There where errors while sending to %r: %r',
                self.socket, error.args
            )
            self.logger.exception(error)
        finally:
            del(client)
            self.executed = True


class SendNativeWorker(Thread):
    def __init__(self, in_queue, stop_event, ssl_key, ssl_cert, ssl_ca_cert, max_wait=1, max_results=10, batch_mode=False, timeout=3, default_port=5678):
        super(SendNativeWorker, self).__init__()
        self.name = self.__class__.__name__ +  self.name
        self.in_queue = in_queue
        self.stop_event = stop_event
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        self.ssl_ca_cert = ssl_ca_cert
        self.max_wait = max_wait
        self.max_results = max_results
        self.batch_mode = batch_mode
        self.timeout = timeout
        self.default_port = default_port
        self.out_queue = Queue()
        self.process_joiner = WorkerJoiner(self.out_queue, self.stop_event)
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__module__, self.name)
        )

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
                    worker = self._build_worker(socket, [self._format_result(result)])
                    worker.start()
                    workers.append(worker)
        else:
            self.logger.debug(
                'Sending %s results in batch mode.', len(results)
            )
            batch_mapping = dict()
            for result in results:
                for socket in result['servers'].itervalues():
                    socket = socket.split(':', 1)
                    if len(socket) > 1:
                        socket = '%s:%d' %(socket[0], int(socket[1]))
                    else:
                        socket = '%s:%d' %(socket[0], self.default_port)

                    string_list = batch_mapping.setdefault(socket, list())
                    string_list.append(self._format_result(result))

            for socket, string_list in batch_mapping.iteritems():
                worker = self._build_worker(socket, string_list)
                worker.start()
                workers.append(worker)
        return workers

    def _build_worker(self, socket, message):
        return SendNativeExecutor(
            socket=socket,
            message=message,
            ssl_key=self.ssl_key,
            ssl_cert=self.ssl_cert,
            ssl_ca_cert=self.ssl_ca_cert,
            timeout=self.timeout
        )

    def run(self):
        self.logger.debug('Starting %r thread ...', self.process_joiner.name)
        self.process_joiner.start()
        self.logger.debug('%r thread started.', self.process_joiner.name)
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

            self.logger.debug('Shutting down ...')

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

    def _format_result(self, result, delim=';'):
        check_type = result['check_type']
        check_hostname = result['check_hostname']
        check_returncode = result['check_result']['returncode']
        check_msg = result['check_result']['stdout']

        if check_type == 'host_check':
            ### PROCESS_HOST_CHECK_RESULT ###
            # [time] PROCESS_HOST_CHECK_RESULT;<host_name>;<status_code>;<plugin_output>
            return '[%d] PROCESS_HOST_CHECK_RESULT;%s%s%s%s%s' %(
                time(), check_hostname, delim, check_returncode, delim, check_msg
                )

        if check_type == 'service_check':
            ### PROCESS_SERVICE_CHECK_RESULT ###
            # [time] PROCESS_SERVICE_CHECK_RESULT;<host_name>;<service_description>;<return_code>;<plugin_output>
            check_description = result['check_description']
            return '[%d] PROCESS_SERVICE_CHECK_RESULT;%s%s%s%s%s%s%s' %(
                time(),
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