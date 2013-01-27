#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

__author__ = 'Robin Wittler'
__contact__ = 'r.wittler@mysportgroup.de'
__license__ = 'GPL3+'
__copyright__ = '(c) 2013 by mysportgroup.de'
__version__ = '0.0.1'

import os
import sys
import pwd
import grp
import stat


def is_somehow_writeable_for_uid(path, uid):
    user_struct = pwd.getpwuid(uid)
    return is_somehow_writeable_for_user_struct(path, user_struct)

def is_somehow_writeable_for_username(path, username):
    user_struct = pwd.getpwnam(username)
    return is_somehow_writeable_for_user_struct(path, user_struct)

def is_somehow_readable_for_uid(path, uid):
    user_struct = pwd.getpwuid(uid)
    return is_somehow_readable_for_user_struct(path, user_struct)

def is_somehow_readable_for_username(path, username):
    user_struct = pwd.getpwnam(username)
    return is_somehow_readable_for_user_struct(path, user_struct)

def is_somehow_writeable_for_user_struct(path, user_struct):
    return mode_applies_somehow_on_path_for_user_struct(stat.S_IWRITE, path, user_struct)

def is_somehow_readable_for_user_struct(path, user_struct):
    return mode_applies_somehow_on_path_for_user_struct(stat.S_IREAD, path, user_struct)

def mode_applies_somehow_on_path_for_user_struct(mode, path, user_struct):
    mode_map = {
        stat.S_IWRITE: [stat.S_IWUSR, stat.S_IWGRP, stat.S_IWOTH, os.W_OK],
        stat.S_IREAD: [stat.S_IRUSR, stat.S_IRGRP, stat.S_IROTH, os.R_OK],
        stat.S_IEXEC: [stat.S_IXUSR, stat.S_IXGRP, stat.S_IXOTH, os.X_OK],
        stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC: [
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR,
            stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP,
            stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH,
            os.R_OK | os.W_OK | os.X_OK
        ],
        stat.S_IREAD | stat.S_IWRITE: [
            stat.S_IRUSR | stat.S_IWUSR,
            stat.S_IRGRP | stat.S_IWGRP,
            stat.S_IROTH | stat.S_IWOTH,
            os.R_OK | os.W_OK
        ],
        stat.S_IREAD | stat.S_IEXEC: [
            stat.S_IRUSR | stat.S_IXUSR,
            stat.S_IRGRP | stat.S_IXGRP,
            stat.S_IROTH | stat.S_IXOTH,
            os.R_OK | os.X_OK
        ],
        stat.S_IWRITE | stat.S_IEXEC: [
            stat.S_IWUSR | stat.S_IXUSR,
            stat.S_IWGRP | stat.S_IXGRP,
            stat.S_IWOTH | stat.S_IXOTH,
            os.W_OK | os.X_OK
        ]
    }

    if mode not in mode_map:
        raise KeyError(
            'There is no such mode: %r' %(mode,)
        )

    if user_struct.pw_uid in (os.getuid(), os.geteuid()):
        os.access(path, mode_map.get(mode)[3])

    path_stat = os.stat(path)
    group = grp.getgrgid(path_stat.st_gid)

    if path_stat.st_uid == user_struct.pw_uid:
        if path_stat.st_mode & mode_map.get(mode)[0] != 0:
            return True

    if path_stat.st_gid == user_struct.pw_gid or user_struct.pw_name in group.gr_mem:
        if path_stat.st_mode & mode_map.get(mode)[1] != 0:
            return True

    return path_stat.st_mode & mode_map.get(mode)[2] != 0





if __name__ == '__main__':
    pass


    # vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4