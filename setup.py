#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
from distutils.core import setup


setup(
        name='massive-passive',
        version='0.2.1',
        description='A scheduler for passive nagios/icinga checks.',
        author='Robin Wittler',
        author_email='r.wittler@mysportgroup.de',
        maintainer='Robin Wittler',
        maintainer_email='r.wittler@mysportgroup.de',
        license='GPL3+',
        url='https://github.com/mysportgroup/massive-passive',
        install_requires=['simplejson', 'apscheduler', 'psutil', 'setproctitle'],
        packages=['mplib'],
        data_files=[
            ('/usr/sbin', ['massive-passive']),
            ('/etc/massive-passive/checks.d', ['etc/massive-passive/checks.d/first_check.cfg', 'etc/massive-passive/checks.d/second_check.cfg']),
            ('/etc/init.d', ['etc/init.d/massive-passive']),
            ('/etc/default', ['etc/default/massive-passive']),
            ('/usr/share/massive-passive', ['LICENSE.txt', 'README.txt']),
        ],
        platforms='POSIX',
)



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
