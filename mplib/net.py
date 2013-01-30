#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__copyright__ = '(c) 2013 by mysportgroup.de'
__version__ = '0.0.1'

import os
import sys
import logging
import base64
from OpenSSL import SSL
from twisted.internet import ssl
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import connectionDone
from twisted.internet.protocol import ClientFactory

logger = logging.getLogger(__name__)

class ExternalCommandWriterProtocol(Protocol):
    def __init__(self, external_command_file, **kwargs):
        self.external_command_file = external_command_file
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )

    def dataReceived(self, data):
        decoded_data = base64.decodestring(data)
        self.logger.debug('Received data from %s: %r', self.transport.getPeer(), decoded_data)
        state = self.writeToCommandFile(decoded_data)
        self.logger.debug(
            'Sending %r to %s.',
            state, self.transport.getPeer()
        )
        self.transport.write(base64.encodestring(state))

    def writeToCommandFile(self, data):
        try:
            with open(self.external_command_file, 'w') as fh:
                fh.write(data)
        except Exception as error:
            self.logger.error(
                'There was an error while writing data to %r',
                self.external_command_file
            )
            self.logger.exception(error)
            state = 'ERROR %s\n' %(error,)
        else:
            len_data = len(data)
            self.logger.debug(
                'Written %d bytes to %r',
                len_data, self.external_command_file
            )
            state = 'OK %d bytes received and written.\n' %(len_data,)

        return state

    def connectionLost(self, reason=connectionDone):
        self.logger.info(
            'Connection lost event for %s. Reason: %s',
            self.transport.getPeer(), reason.getErrorMessage()
        )

        self.transport.loseConnection()
        self.transport = None

class ExternalCommandWriterFactory(Factory):
    protocol = ExternalCommandWriterProtocol
    
    def __init__(self, external_command_file):
        self.external_command_file = external_command_file
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )

    def buildProtocol(self, addr):
        self.logger.info('Build protocol for %r', addr)
        return self.protocol(
            self.external_command_file,
        )


class SSLCallbacks(object):
    def __init__(self):
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )
        
    def verifyCallback(self, connection, x509, errnum, errdepth, ok):
        if not ok:
            self.logger.error(
                'Getting invalid cert from %r: %r. ERRNUM: %r, ERRDEPTH: %r',
                connection,
                x509.get_subject(),
                errnum,
                errdepth
            )
            return False
        else:
            self.logger.debug(
                'Received a valid cert %s.',
                x509.get_subject()
            )
        return True

ssl_callbacks = SSLCallbacks()


class SSLServerContextFactory(ssl.DefaultOpenSSLContextFactory):
    def __init__(
            self, privateKeyFileName, certificateFileName, caCertificateFilename,
            sslParanoiaLevel=SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT | SSL.VERIFY_CLIENT_ONCE,
            checkCallback=None, **kwargs
    ):
        ssl.DefaultOpenSSLContextFactory.__init__(self, privateKeyFileName, certificateFileName, **kwargs)
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )
        self.caCertificateFileName = caCertificateFilename
        self.sslParanoiaLevel = sslParanoiaLevel
        self.checkCallback = checkCallback or ssl_callbacks.verifyCallback

    def buildContext(self):
        context = self.getContext()
        context.set_verify(self.sslParanoiaLevel, self.checkCallback)
        context.load_verify_locations(self.caCertificateFileName)
        return context


class PassiveCheckSubmitProtocol(Protocol):
    def __init__(self, data):
        self.data = data
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )

    def connectionMade(self):
        self.logger.debug(
            'Successfully made a connection to %r.',
            self.transport.getPeer()
        )
        self.logger.debug('Data to send is: %r', self.data)
        data = '\n'.join(self.data) + '\n'
        self.logger.debug('Sending %r to %r.', data, self.transport.getPeer())
        self.transport.write(base64.encodestring(data))
        self.logger.info('%d bytes send to %r', len(data), self.transport.getPeer())

    def dataReceived(self, data):
        decoded_data = base64.decodestring(data)
        self.logger.debug('Received this message from %r: %r', self.transport.getPeer(), decoded_data)
        self.logger.debug('Ending connection to %r', self.transport.getPeer())
        self.transport.loseConnection()
        self.transport = None
        self.data = None

class PassiveCheckSubmitFactory(ClientFactory):
    protocol = PassiveCheckSubmitProtocol

    def __init__(self, data, parent):
        self.data = data
        self.parent = parent
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )

    def buildProtocol(self, addr):
        self.logger.debug('Building Protocol for addr %r and data %r.', addr, self.data)
        return self.protocol(data=self.data)

    def clientConnectionFailed(self, connector, reason):
        self.logger.error('Connection to %r failed. Reason: %r', connector.getDestination(), reason)
        self.parent.executed = True
        self.parent = None
        connector = None
        self.data = None

    def clientConnectionLost(self, connector, reason):
        self.logger.error('Connection to %r lost. Reason: %r', connector.getDestination(), reason)
        self.parent.executed = True
        self.parent = None
        connector = None
        self.data = None

    def stopFactory(self):
        del(self.data)
        del(self.parent)



class SSLClientContextFactory(ssl.ClientContextFactory):
    def __int__(self):
        self.cert_path = None
        self.key_path = None
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )

    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        context = ssl.ClientContextFactory.getContext(self)
        context.use_certificate_file(self.cert_path)
        context.use_privatekey_file(self.key_path)
        return context

if __name__ == '__main__':
    pass


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4