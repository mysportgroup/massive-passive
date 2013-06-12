#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
from distutils.core import setup


setup(
        name='massive-passive',
        version='0.3.7',
        description='A scheduler for passive nagios/icinga checks. This includes a server and client.',
        author='Robin Wittler',
        author_email='r.wittler@mysportgroup.de',
        maintainer='Robin Wittler',
        maintainer_email='r.wittler@mysportgroup.de',
        license='GPL3+',
        url='https://github.com/mysportgroup/massive-passive',
        install_requires=['simplejson', 'apscheduler', 'setproctitle', 'Twisted', 'pyOpenSSL', 'IPy', 'pyinotify'],
        packages=['mplib', 'mplib.net', 'mplib.getopts', 'mplib.threads'],
        data_files=[
            ('/usr/sbin', ['massive-passive-client', 'massive-passive-server']),
            ('/etc/massive-passive/checks.d', ['etc/massive-passive/checks.d/first_check.cfg', 'etc/massive-passive/checks.d/second_check.cfg']),
            ('/etc/massive-passive/allowed-client-cert.d', []),
            ('/etc/init.d', ['etc/init.d/massive-passive-client', 'etc/init.d/massive-passive-server']),
            ('/etc/default', ['etc/default/massive-passive-client', 'etc/default/massive-passive-server']),
            ('/usr/share/massive-passive-client', ['LICENSE.txt', 'README.txt']),
            ('/usr/share/massive-passive-server', ['LICENSE.txt', 'README.txt']),
        ],
        platforms='POSIX',
)



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
