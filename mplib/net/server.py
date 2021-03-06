#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__copyright__ = '(c) 2013 by mysportgroup.de'
__version__ = '0.0.3'

import os
import base64
import logging
from glob import glob
from OpenSSL import SSL
from threading import Lock
from twisted.internet import ssl
from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import load_certificate
from OpenSSL.crypto import Error as SSLError
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import connectionDone

from cStringIO import StringIO


logger = logging.getLogger(__name__)


class ExternalCommandWriterProtocol(Protocol):
    def __init__(self, external_command_file, buffers, batch_mode=True, **kwargs):
        self.external_command_file = external_command_file
        self.buffers = buffers
        self.batch_mode = batch_mode
        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )

    def connectionMade(self):
        self.buffer, self.propagated_len_data, self.chunked_data = \
            self.buffers.setdefault(
                self.transport.getPeer(),
                [StringIO(), 0, False]
            )
        self.logger.debug(
            'Create buffer for %s: %r',
            self.transport.getPeer(),
            (
                self.buffer,
                self.propagated_len_data,
                self.chunked_data
            )
        )

    def dataReceivedOldProtocol(self, data):
        decoded_data = base64.decodestring(data)
        self.logger.debug('Received data from %s: %r', self.transport.getPeer(), decoded_data)
        state = self.writeToCommandFile(decoded_data)
        self.logger.debug(
            'Sending %r to %s.',
            state, self.transport.getPeer()
        )
        self.transport.write(base64.encodestring(state))

    def dataReceived(self, data):
        '''
        This version handles the new protocol (with len header)
        '''

        len_data = len(data)

        if not self.chunked_data:
            # must be initial data
            self.logger.debug(
                'Received initial data with len %d from %s',
                len_data,
                self.transport.getPeer()
            )
            self.reset_buffer()
            try:
                self.propagated_len_data, data = data.split(' ', 1)
            except ValueError:
                # so the format is not like "len_count <base64_data>
                # and therefor we assume that the message is send in the
                # old format.
                self.logger.error(
                    'Received a message in the old format.'
                )
                return self.dataReceivedOldProtocol(data)
            self.propagated_len_data = int(self.propagated_len_data)
            self.logger.debug(
                'Propagated len from %s is %d',
                self.transport.getPeer(),
                self.propagated_len_data
            )
            self.buffer.write(data)

            if self.propagated_len_data == self.buffer.tell():
                # we received the complete message at once
                self.logger.debug(
                    'Received all data at once from %s',
                    self.transport.getPeer()
                )
            else:
                # ok - we receive the complete message in multiple chunks
                self.logger.debug(
                    'Received data from %s is a chunk starter. ' +
                    'We miss %d bytes',
                    self.transport.getPeer(),
                    self.propagated_len_data - self.buffer.tell()
                )
                self.chunked_data = True

                self.update_buffer(
                    self.transport.getPeer(),
                    self.buffer,
                    self.propagated_len_data,
                    self.chunked_data
                )
                return
        else:
            # must be a chunk of data
            self.logger.debug(
                'Received another chunk of data with len %d from %s',
                len_data,
                self.transport.getPeer()
            )
            self.buffer.write(data)
            if self.propagated_len_data != self.buffer.tell():
                self.logger.debug(
                    'Chunk from %s is not complete. ' +
                    'We miss %d bytes.',
                    self.transport.getPeer(),
                    self.propagated_len_data - self.buffer.tell()
                )
                self.update_buffer(
                    self.transport.getPeer(),
                    self.buffer,
                    self.propagated_len_data,
                    self.chunked_data
                )
                return
            else:
                self.logger.debug(
                    'All chunks from %s are received.',
                    self.transport.getPeer()
                )

        self.buffer.seek(0, 0)
        decoded_data = base64.decodestring(self.buffer.read())
        self.reset_buffer()
        self.writeToCommandFile(decoded_data)

    def writeToCommandFile(self, data):
        if not os.path.exists(self.external_command_file):
            self.logger.error(
                'External command file at %r does not exists. Is icinga/nagios running?',
                self.external_command_file
            )
            state = 'ERROR Could not write to external command file.\n'
        else:
            try:
                with open(self.external_command_file, 'w+') as fh:
                    if self.batch_mode:
                        fh.write(data)
                        fh.flush()
                    else:
                        for line in data.split('\n'):
                            fh.write(line + '\n')
                            fh.flush()
            except Exception as error:
                self.logger.error(
                    'There was an error while writing data to %r',
                    self.external_command_file
                )
                self.logger.exception(error)
                state = 'ERROR %s\n' %(error,)
            else:
                len_data = len(data)
                self.logger.info(
                    'Written %d bytes to %r received through %r',
                    len_data, self.external_command_file, self.transport.getPeer()
                )
                state = 'OK %d bytes received and written.\n' %(len_data,)
        return state

    def connectionLost(self, reason=connectionDone):
        self.logger.info(
            'Connection lost event for %s. Reason: %s',
            self.transport.getPeer(), reason.getErrorMessage()
        )

        self.remove_buffer()
        self.transport.loseConnection()
        self.transport = None

    def reset_buffer(self):
        self.buffer.seek(0, 0)
        self.buffer.truncate()

    def remove_buffer(self):
        peer = self.buffers.pop(self.transport.getPeer(), None)
        self.logger.debug(
            'Removing buffer of peer %s which was: %r',
            self.transport.getPeer(),
            peer
        )

    def update_buffer(self, key, *values):
        return self.buffers.update({key: values})


class ExternalCommandWriterFactory(Factory):
    protocol = ExternalCommandWriterProtocol
    buffers = dict()

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
            self.buffers
        )


class SSLValidationStore(object):
    def __init__(self, basedir, cacert):
        if os.path.exists(basedir):
            if not os.path.isdir(basedir):
                raise RuntimeError(
                    '%r is not a directory' %(basedir)
                )
        else:
            raise RuntimeError('%r does not exists.' %(basedir))
        self.basedir = basedir

        if not os.path.exists(cacert):
            raise RuntimeError('%r does not exists.' %(cacert))

        with open(cacert, 'r', 1) as  fp:
            self.cacert = load_certificate(FILETYPE_PEM, fp.read())

        #try:
        #    self.cacert_key_identifier = self.cacert.get_extension(1).get_data()
        #except AttributeError:
        #    # the debian squeeze python-openssl version has no get_extension attribute :(
        #    # so ... we set cacert_key_identifier to None.
        #    # On later code we check if this attr is None, if so, we only check subject string.
        self.cacert_key_identifier = None

        self._store_lock = Lock()
        self._store = dict()

        self.logger = logging.getLogger(
            '%s.%s'
            %(self.__class__.__module__, self.__class__.__name__)
        )

        self.add_pems_from_basedir()

    def join_cert_subject_components(self, cert):
        return '/' + '/'.join(
            ['%s=%s' %(i[0], i[1]) for i in cert.get_subject().get_components()]
        )

    def is_cert_from_ca(self, cert):
        try:
            return cert.get_extension(3).get_data() == self.cacert_key_identifier
        except IndexError:
            return False

    def load_pem(self, filename):
        self.logger.debug('Trying to load %r.', filename)
        try:
            with open(filename, 'r', 1) as fp:
                    cert = load_certificate(FILETYPE_PEM, fp.read())
        except Exception as error:
            self.logger.info(
                'Could not load certificate from %r. Error was: %r',
                filename,
                error
            )
            return None
        else:
            self.logger.debug(
                'Successfully loaded certificate from %r',
                filename
            )
            return cert

    def validate_cert_ca(self, cert):
        if self.cacert_key_identifier is not None and not self.is_cert_from_ca(cert):
            return False
        return True

    def add_cert_info_to_store(self, filename, cert):
        cert_subject_components = self.join_cert_subject_components(cert)
        if self.cacert_key_identifier is not None:
            subject_key_identifier = cert.get_extension(2).get_data()
        else:
            subject_key_identifier = None

        cert_dict = dict(filename=filename, subject_key_identifier=subject_key_identifier)

        self.logger.info(
            'Adding (%r, %r) to store.', cert_subject_components, cert_dict
        )

        self._store_lock.acquire()
        try:
            self._store.update({cert_subject_components: cert_dict})
        finally:
            self._store_lock.release()

    def add_pems_from_basedir(self):
        for filename in glob(os.path.join(self.basedir, '*.pem')):
            self.add_pem(filename)

    def add_pem(self, filename):
        cert = self.load_pem(filename)
        if cert is None:
            return False

        if self.validate_cert_ca(cert) is False:
            self.logger.info(
                'Authority Key Identifier mismatch for certificate %r. Ignoring certificate.',
                filename
            )
            return False

        self.add_cert_info_to_store(filename, cert)
        return True

    def remove_pem(self, filename):
        self._store_lock.acquire()
        try:
            for cert_subject_components, cert_dict in self._store.iteritems():
                if cert_dict.get('filename') == filename:
                    self.logger.info(
                        'Removing %r (filename: %r) from store.', cert_subject_components, filename
                    )
                    self._store.pop(cert_subject_components)
                    break
            else:
                self.logger.info(
                    'Could not found a cert for %r in store.', filename
                )
        finally:
            self._store_lock.release()

    def validate_cert(self, cert):
        cert_subject_components = self.join_cert_subject_components(cert)
        self.logger.debug('Looking for %r', cert_subject_components)
        self._store_lock.acquire()
        try:
            validation_data = self._store.get(cert_subject_components, None)
        finally:
            self._store_lock.release()

        if validation_data is None:
            self.logger.info('No file found for certificate: %r', cert.get_subject())
            return False

        filename = validation_data.get('filename')

        if self.cacert_key_identifier is not None:
            subject_key_identifier = validation_data.get('subject_key_identifier')
            if subject_key_identifier != cert.get_extension(2).get_data():
                self.logger.info(
                    'SubjectKeyIdentifier of %r mismatch received certificate %r',
                    filename,
                    cert.get_subject()
                )
                return False
            else:
                self.logger.debug(
                    'SubjectKeyIdentifier of certificate %r matches received SubjectKeyIdentifier of certificate %r',
                    filename,
                    cert.get_subject()
                )
        self.logger.info('Certificate %r is authorized through file %r. Go ahead.', cert.get_subject(),filename)
        return True


class SSLCallbacks(object):
    def __init__(self, validation_store):
        self.validation_store = validation_store
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
            subject = x509.get_subject()
            issuer = x509.get_issuer()
            if subject == issuer:
                self.logger.debug(
                    'Received a valid ca certificate %s',
                    subject
                )
            else:
                if self.validation_store.validate_cert(x509):
                    self.logger.debug(
                        'Received a valid certificate %s.',
                        subject
                    )
                else:
                    self.logger.info(
                        '%r is a valid signed certificate, but it is not allowed to send data.',
                        x509.get_subject()
                    )
                    return False
        return True



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
        self.checkCallback = checkCallback

    def buildContext(self):
        context = self.getContext()
        context.set_verify(self.sslParanoiaLevel, self.checkCallback)
        context.load_verify_locations(self.caCertificateFileName)
        return context


if __name__ == '__main__':
    pass


    # vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4