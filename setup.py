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
        install_requires=['python-debian', 'simplejson', 'apscheduler'],
        packages=['mplib'],
        data_files=[
            ('/usr/sbin', ['massive-passive']),
            ('/etc/massive-passive/checks.d', ['checks.d/first_check.cfg', 'checks.d/second_check.cfg']),
            ('/usr/share/massive-passive', ['LICENSE.txt', 'README.txt']),
        ],
        platforms='POSIX',
)



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
