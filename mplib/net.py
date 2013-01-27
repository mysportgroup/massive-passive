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
from time import time
from OpenSSL import SSL
from Queue import Empty
from twisted.internet import ssl
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import connectionDone
from twisted.internet.protocol import ClientFactory

logger = logging.getLogger(__name__)

### PROCESS_HOST_CHECK_RESULT ###

# PROCESS_HOST_CHECK_RESULT;<host_name>;<status_code>;<plugin_output>

# This is used to submit a passive check result for a particular host. The "status_code" indicates
# the state of the host check and should be one of the following: 0=UP, 1=DOWN, 2=UNREACHABLE.
# The "plugin_output" argument contains the text returned from the host check, along with optional
# performance data.

### PROCESS_SERVICE_CHECK_RESULT ###

# PROCESS_SERVICE_CHECK_RESULT;<host_name>;<service_description>;<return_code>;<plugin_output>

# This is used to submit a passive check result for a particular service. The "return_code" field
# should be one of the following: 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN. The "plugin_output" field
# contains text output from the service check, along with optional performance data.

EXTERNAL_COMMAND_FILE = '/var/lib/icinga/rw/icinga.cmd'

class ExternalCommandWriterProtocol(Protocol):
    def __init__(self, external_command_file):
        self.external_command_file = external_command_file
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )

    def dataReceived(self, data):
        self.logger.debug('Received data from %s: %r', self.transport.getPeer(), data)
        state = self.writeToCommandFile(data)
        self.logger.debug(
            'Sending %r to %s.',
            state, self.transport.getPeer()
        )
        self.transport.write(state)

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
            state = 'FAIL %s\n' %(error,)
        else:
            len_data = len(data)
            self.logger.debug(
                'Written %d bytes to %r',
                len_data, self.external_command_file
            )
            state = 'OK %d\n' %(len_data,)

        return state

    def connectionLost(self, reason=connectionDone):
        self.logger.info(
            'Connection lost event for %s. Reason: %s',
            self.transport.getPeer(), reason
        )

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
        return self.protocol(self.external_command_file)


class SSLCallbacks(object):
    def __init__(self):
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )
        
    def verifyCallback(self, connection, x509, errnum, errdepth, ok):
        if not ok:
            self.logger.info(
                'Getting invalid cert from %r: %r. ERRNUM: %r, ERRDEPTH: %r',
                connection,
                x509.get_subject(),
                errnum,
                errdepth
            )
            return False
        else:
            self.logger.info(
                'Received a good cert from %r.',
                connection
            )
        return True

ssl_callbacks = SSLCallbacks()

class SSLClientContextFactory(ssl.ClientContextFactory):
    def __init__(self, certificate_path, privatekey_path):
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )
        self.certificate_path = certificate_path
        self.privatekey_path = privatekey_path

    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        context = ssl.ClientContextFactory.getContext(self)
        context.use_certificate_file(self.certificate_path)
        context.use_privatekey_file(self.privatekey_path)
        return context





#if __name__ == '__main__':
#    factory = Factory()
#    factory.protocol = ExternalCommandWriter

#    myContextFactory = ssl.DefaultOpenSSLContextFactory(
#        '/home/real/ssltest/sslCA/private/server-key.pem', '/home/real/ssltest/sslCA/server-cert.pem'
#    )

#    ctx = myContextFactory.getContext()

#    ctx.set_verify(
#        SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
#        verifyCallback
#    )

    # Since we have self-signed certs we have to explicitly
    # tell the server to trust them.
#    ctx.load_verify_locations("/home/real/ssltest/sslCA/cacert.pem")
#    reactor.listenSSL(8000, factory, myContextFactory)
#    reactor.run()

#testdata = [
#   'PROCESS_SERVICE_CHECK_RESULT;localhost;testservice;0;Alles ok!|performane_value=5:10',
#   'PROCESS_SERVICE_CHECK_RESULT;localhost2;testservice;0;Alles ok die zweite!|performane_value=8:10'
#

#class PassiveCheckSubmitProtocol(Protocol):
#   def connectionMade(self):
#       print "connectionMade"
#       self.transport.write('\n'.join(testdata) + '\n')

#   def dataReceived(self, data):
#       print "dataReceived: %r" %(data,)
#       self.transport.loseConnection()

#class PassiveCheckSubmitFactory(ClientFactory):
#   protocol = PassiveCheckSubmitProtocol

#   def clientConnectionFailed(self, connector, reason):
#       print "Connection failed - bye! connector => %r, reason => %r" %(connector, reason)
#       reactor.stop()

#   def clientConnectionLost(self, connector, reason):
#       print "Connection lost - bye! connector => %r, reason => %r" %(connector, reason)
#       reactor.stop()


#class ContextFactory(ssl.ClientContextFactory):
#   def getContext(self):
#       self.method = SSL.SSLv23_METHOD
#       ctx = ssl.ClientContextFactory.getContext(self)
#       ctx.use_certificate_file('/home/real/ssltest/sslCA/server-cert.pem')
#       ctx.use_privatekey_file('/home/real/ssltest/sslCA/private/server-key.pem')

#       # wrong certiticates for testing
#       #ctx.use_certificate_file('/home/real/ssltest/wrong-client-cert.pem')
#       #ctx.use_privatekey_file('/home/real/ssltest/wrong-client-key.pem')

#       return ctx

#if __name__ == '__main__':
#    factory = PassiveCheckSubmitFactory()
#    reactor.connectSSL('127.0.0.1', 8000, factory, ContextFactory())
#    reactor.run()



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4