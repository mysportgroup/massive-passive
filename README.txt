===============
massive-passive
===============

A scheduler for passive nagios/icinga checks.
massive-passive is a simple scheduler for passive nagios/icinga checks.
At the moment it uses send_nsca for sending data to nagios/icinga (other 
methods are planned, like stuff from mod_gearman (send_gearman?), a own
listener and maybe even delivery via cgi (if someone needs this).

 

Why a scheduler for passive nagios/icinga checks and not using cron?
--------------------------------------------------------------------

Cron is good. But it can not execute passive checks every 5 seconds.
massive-passive can execute multiple passive checks every "n" second.
So you can execute one check every 5 seconds, another every 7 seconds, and
several other every 30 seconds, and so on. From Version 0.2.10 on, it is
possible to say:

    Execute this job every day and every hour between 9 and 17 (office workhours),
    beginning at the date 2099-11-11 11:11:11

You can also just use every existing normal nagios/icinga host and service
check (if written with the standard rules for nagios/icinga checks in mind)
and execute it via massive-passive. The result of a check will be translated
in the correct nsca format and send to (maybe multiple) nagios/icinga hosts.
And if you want, this will be done in batch mode. So you could send e.g.
5 results in one nsca connection.

Also you don't have to deal with lock files. Imagine you have a long running
check - and the execution Time is somewhat a moving target. But the check must
run as a single instance and not multiple instance at the same time.
Normally you extend your passive check with a lock file function or other
mechanism, to ensure that it only runs once a time. With massive-passive you
don't have to do this. The apscheduler (thanks to Alex Grönholm) behind
massive-passive ensures it on it's own. But - if you want several running
instances of your check, you can do that, too. Just configure your check
with the "max_instances" parameter with a value greater then 1 and it's done.
All this does not work out-of-the-box with cron.

So just configure your nagios/icinga check and have fun!



How?
----

Get the source from github (https://github.com/mysportgroup/massive-passive).
Make sure you have python and python setuptools installed.
Do:

    Configure your nsca daemon and send_nsca client.

    cd /path/to/massive-passive-source
    python setup.py install

    now start the daemon:
    /etc/init.d/massive-passive start

    on debian you could do:
    service massive-passive start

Then take a look at /etc/massive-passive/checks.d/
Checks configuration is done via a simple JSON configfile for every check.
There are already two sample checks in this directory. Both have non valid JSON 
data inside, so those checks won't be used.

Use them as a template. The needed config options are somewhat self explaining.
But for a better understanding we take a closer look at them.


{
    "check_description": "First passive check",
    "interval": 25,
    "servers":
           {
                    "nagios-host-1": "127.0.0.1:5667",
                    "icinga-host-1": "127.0.1.1:9999",
                    "icinga-host-2": "10.10.10.1"
            },
    "command": "/bin/echo 'hello this is an environment test: $TESTERTEST'",
    "env": {"TESTERTEST": "moep!"},
    "check_type": "service_check",
    "check_hostname": "this.is.a.hostname",
    "max_instances": 3
}

check_description: This is the check description also used on side of the nagios/icinga server.
It is necessary that you use the same description on both sides (nagios/icinga side and on 
massive-passive side)

interval: this interval is used to execute your checks (in seconds)

servers: you can add as many servers as needed. if they use the default nsca port (port 5667)
you can write:
     "hostname": "ipaddress"
if a different port is needed than you can write:
    "hostname": "ipaddress:port"

command: This is the command (the check) you want to be executed.
You can write it down just like you did it in your shell. You can also make use of
environment variables (maybe to set some password or other stuff).

env: with env you can set special environment variables for your check.
The default is: env is empty! (there is no $PATH, $HOME, etc pp)

check_type: There are two different check types: host and service checks.

check_hostname: The hostname for this check. Must be equal with the hostname
configured on the nagios/icinga side.

max_instances: The maximum of running instances of a check at the same time. (default 1)

At version 0.2.10 it also possible to do something like this:
-------------------------------------------------------------

{
    "check_description": "First passive check",
    "interval":
           {
                    "hour": "9-17",
                    "day": "1-12,24-30",
                    "start_date": "2099-11-11 11:11:11"
           }
    "servers":
           {
                    "nagios-host-1": "127.0.0.1:5667",
                    "icinga-host-1": "127.0.1.1:9999",
                    "icinga-host-2": "10.10.10.1"
            },
    "command": "/bin/echo 'hello this is an environment test: $TESTERTEST'",
    "env": {"TESTERTEST": "moep!"},
    "check_type": "service_check",
    "check_hostname": "this.is.a.hostname",
    "max_instances": 3
}

which means:
    process this check every day on the 1 to 12 and 24 to 30 of the month,
    between 9 and 17 and do it first at the 2099-11-11 11:11:11.


After configuring your first check, you can do:
    kill -1 <PID OF MASSIVE-PASSIVE> 

    or

    /etc/init.d/massive-passive reload

    or (on debian)
    
    service massive-passive reload
to reload the configs at runtime. 



All command line options for starting massive-passive:
------------------------------------------------------

Usage: massive-passive [options]

massive_passive is a tool for scheduling passive nagios/icinga checks.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -f, --foreground      Do not run in Background. Default: False
  -l LOGLEVEL, --loglevel=LOGLEVEL
                        The loglevel to use. Default: INFO
  --confdir=CONFDIR     The path to the passive check configurations
                        directory. Default: /etc/massive-passive/checks.d
  --pidfile=PIDFILE     The path to the pidfile (if running in Background).
                        Default: /tmp/massive-passive.pid
  --batch-mode          Use batch mode for sending passive check results?
                        Default: False
  --batch-wait-time=BATCH_WAIT_TIME
                        Set the max wait time before sending check results in
                        batch mode. Default: 2
  --batch-max-items=BATCH_MAX_ITEMS
                        How much items to use in batch mode. A value of 0
                        means unlimited items. Default: 10
  -u USER, --user=USER  The username who should execute this process. Default:
                        <the actual username>
  -g GROUP, --group=GROUP
                        The groupname this process runs at. Default: <the actual group name>
  --initial-random-wait-range=INITIAL_RANDOM_WAIT_RANGE
                        The seconds to random wait before the scheduler
                        executes the jobs the first time. This only applies
                        when starting or reloading the scheduler. The wait
                        range goes from: 2 to INITIAL_RANDOM_WAIT_RANGE. If
                        set to 0, there is no range and every check will be
                        initially scheduled after 2 seconds (which can produce
                        some load). Default: 10
  --logfile=LOGFILE     The path to the logfile. Default: /tmp/massive-
                        passive.log
  --path-to-send-nsca=PATH_TO_SEND_NSCA
                        The path to the send_nsca binary. Default:
                        /usr/sbin/send_nsca

author: Robin Wittler <r.wittler@mysportgroup.de>  Copyright (C) 2012 by
mysportgroup.de  This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.  This program is distributed in the hope that it
will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
Public License for more details.  You should have received a copy of the GNU
General Public License along with this program.  If not, see
<http://www.gnu.org/licenses/>.



A brief documentation will follow. Thank you and have fun!


TODO:
-----

    * write a Documentation
    * write a own transport channel to get rid of nsca/send_nsca
      This channel should support ssl client auth.
    * Make it possible that the massive-passive client can configure it's checks
      on it's own - based on the nagios/icinga config. This feature can be switched of.


