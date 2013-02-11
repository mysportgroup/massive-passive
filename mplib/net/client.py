#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__copyright__ = '(c) 2013 by mysportgroup.de'
__version__ = '0.0.1'

import ssl
import socket
import logging
import base64

logger = logging.getLogger(__name__)

class PassiveCheckSubmitClient(object):
    def __init__(self, message, ip, ssl_key, ssl_cert, ssl_ca_cert, port=5678, timeout=3):
        self.message = message
        self.ip = ip
        self.port = port
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        self.ssl_ca_cert = ssl_ca_cert
        self.timeout = timeout
        self.sock = None
        self.ssl_sock = None
        self.peer_cert = None
        self.connected = False
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )

    def run(self):
        self.connect()
        len_message, len_encoded_message, len_send_message = self.send_message()
        status, server_received_length, answer = self.receive_answer()
        if server_received_length != len_message:
            self.logger.error(
                'The Server at %r received %d bytes, but our message was %d bytes long.',
                self.ssl_sock.getpeername(),
                server_received_length,
                len_message
            )
        else:
            self.logger.info(
                'Communication with Server at %r was successful.',
                self.ssl_sock.getpeername()
            )
        self.disconnect()

    def start(self):
        return self.run()

    def send_message(self):
        if not self.connected:
            raise ValueError(
                'We are not connected to anyone.'
            )

        encoded_message = base64.encodestring(self.message)
        len_encoded_message = len(encoded_message)
        self.logger.debug('Sending %r to %r.', self.message, self.ssl_sock.getpeername())
        len_send_message = self.ssl_sock.write(
            base64.encodestring(self.message)
        )

        if not len_encoded_message == len_send_message:
            self.logger.error(
                'Byte length of base64 message (%d) and length of bytes (%d) send to %r are not equal.'
                %(len_encoded_message, len_send_message, self.ssl_sock.getpeername())
            )
            return False
        return len(self.message), len_encoded_message, len_send_message

    def receive_answer(self):
        if not self.connected:
            raise ValueError(
                'We are not connected to anyone.'
            )

        encoded_message = self.ssl_sock.read()
        message = base64.decodestring(encoded_message)
        message_list = message.split(' ', 2)
        if message_list[0] != 'OK':
            self.logger.error(
                'The Server %r returned us an error: %r',
                self.ssl_sock.getpeername(),
                message
            )
        elif len(message_list) != 3:
            self.logger.error(
                'Invalid answer from Server at %r received: %r',
                self.ssl_sock.getpeername(),
                message
            )
        else:
            self.logger.debug('Received message from Server at %r: %r',
                self.ssl_sock.getpeername(),
                message
            )

        return message_list[0], int(message_list[1]), message

    def connect(self):
        if not self.connected:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.settimeout(self.timeout)
            self.ssl_sock = ssl.wrap_socket(
                sock=self.sock,
                keyfile=self.ssl_key,
                certfile=self.ssl_cert,
                ca_certs=self.ssl_ca_cert,
                cert_reqs=ssl.CERT_REQUIRED|ssl.PROTOCOL_SSLv23
            )
            self.ssl_sock.connect((self.ip, self.port))
            self.connected = True
            self.peer_cert = self.ssl_sock.getpeercert()
            if not self.peer_cert:
                self.disconnect()
                raise ssl.SSLError(
                    'Received an invalid peer certificate from %r.' %(self.ssl_sock.getpeername(),)
                )
            else:
                self.logger.debug(
                    'Received a valid peer certificate from %r: %r',
                    self.ssl_sock.getpeername(),
                    self.peer_cert
                )
                return True
        else:
            raise ValueError(
                'We are already connected to: %r.' %(self.ssl_sock.getpeername(),)
            )

    def disconnect(self):
        if not self.connected:
            raise ValueError(
                'We are not connected to anyone.'
            )

        self.logger.debug(
            'Closing connection to %r.',
            self.ssl_sock.getpeername()
        )
        self.ssl_sock.unwrap()
        self.sock.shutdown(socket.SHUT_RDWR)
        self.connected = False
        self.sock = None
        self.ssl_sock = None
        return True


if __name__ == '__main__':
    pass


    # vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4