===============
massive-passive
===============

A scheduler for passive nagios/icinga checks.
massive-passive is a simple scheduler for passive nagios/icinga checks.
It is implemented as a client/server architecture and has it's own encrypted
transport channel (as from version 0.3.0) and uses x509 authentification. It
also can be used as a replacement for nsca/send_nsca, because the client has
a --act-as-sender option, which transports every string from stdin to the server.

Using massive-passive as a nsca/send_nsca replacement makes sense, because to get
rid of the byte limitations hardcoded into nsca/send_nsca binaries, which cripples
often performance data or the check message itself.

 

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
and execute it via massive-passive. The result can be send to (maybe multiple)
nagios/icinga hosts. And if you want, this will be done in batch mode.
So you could send e.g. 100 results in one massive-passive connection.

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

For both versions (server and client) do:

    cd /path/to/massive-passive-source
    python setup.py install

Then edit the files with the default start options for the server and client.
They are under /etc/default/massive-passive-(client, server)

For the client do now:
    /etc/init.d/massive-passive-client start

    on debian you could do:
    service massive-passive-client start


For the server do now:
    /etc/init.d/massive-passive-server start

    on debian you could do:
    service massive-passive-server start




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

servers: you can add as many servers as needed. if they use the default massive-passive port (port 5678)
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
                    "nagios-host-1": "127.0.0.1:5678",
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


HINT
----

From massive-passive version 0.3.2 on you don't have to reload the massive-passive-client by hand.
The client watches the confdir and removes/add config changes on it's own.




All command line options for starting massive-passive-server:
-------------------------------------------------------------

Usage: massive-passive-server [options]

massive-passive is a client/server toolset for scheduling passive
nagios/icinga checks. This is the server programm which receives the check
results and write them into the nagios/icinga external command file.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --listen=LISTEN       The ip to listen on. At this moment it is only
                        possible to listen at ipv4 or ipv6 - not both at the
                        same time. This limitation will go away in one of the
                        next releases. Default: 0.0.0.0
  --port=PORT           The port to listen on. Default: 5678
  -f, --foreground      Do not run in Background. Default: False
  -l LOGLEVEL, --loglevel=LOGLEVEL
                        The loglevel to use. Default: INFO
  --pidfile=PIDFILE     The path to the pidfile (if running in Background).
                        Default: /tmp/massive-passive-server.pid
  -u USER, --user=USER  The username who should execute this process. Default:
                        real
  -g GROUP, --group=GROUP
                        The groupname this process runs at. Default: real
  --logfile=LOGFILE     The path to the logfile. Default: /tmp/massive-
                        passive-server.log
  --command-file=COMMAND_FILE
                        The path to the nagios/icinga external command file.
                        If not set, it defaults to one of
                        /var/lib/icinga/rw/icinga.cmd or
                        /var/lib/nagios/rw/nagios.cmd - depending which of
                        them exists.
  --ssl-ca-cert=SSL_CA_CERT
                        The path to the ssl ca cert. Default: /etc/massive-
                        passive/massive-passive-ssl-ca.cert
  --ssl-key=SSL_KEY     The path to the server ssl key file. Default: /etc
                        /massive-passive/massive-passive-server-ssl.key
  --ssl-cert=SSL_CERT   The path to the server ssl cert file. Default: /etc
                        /massive-passive/massive-passive-server-ssl.cert
  --allowed-client-cert-dir=ALLOWED_CLIENT_CERT_DIR
                        Only clients with valid certificates in this dir are
                        allowed to send results. Just put the client certs
                        into this dir to authorize them. Default: /etc
                        /massive-passive/allowed-client-cert.d

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


All command line options for starting massive-passive-client:
-------------------------------------------------------------

Usage: massive-passive-client [options]

massive-passive is a client/server toolset for scheduling passive
nagios/icinga checks. This is the client programm which schedules the checks
and sends the results to the massive-passive-server

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -f, --foreground      Do not run in Background. Default: False
  -l LOGLEVEL, --loglevel=LOGLEVEL
                        The loglevel to use. Default: INFO
  --logfile=LOGFILE     The path to the logfile. Default: /tmp/massive-
                        passive-client.log
  --silent              Do not log to stdout. Default: False
  --confdir=CONFDIR     The path to the passive check configurations
                        directory. Default: /etc/massive-passive/checks.d
  --pidfile=PIDFILE     The path to the pidfile (if running in Background).
                        Default: /tmp/massive-passive-client.pid
  --batch-mode          Use batch mode for sending passive check results?
                        Default: False
  --batch-wait-time=BATCH_WAIT_TIME
                        Set the max wait time before sending check results in
                        batch mode. Default: 2
  --batch-max-items=BATCH_MAX_ITEMS
                        How much items to use in batch mode. A value of 0
                        means unlimited items. Default: 100
  -u USER, --user=USER  The username who should execute this process. Default:
                        real
  -g GROUP, --group=GROUP
                        The groupname this process runs at. Default: real
  --initial-random-wait-range=INITIAL_RANDOM_WAIT_RANGE
                        The seconds to random wait before the scheduler
                        executes the jobs the first time. This only applies
                        when starting or reloading the scheduler. The wait
                        range goes from: 2 to INITIAL_RANDOM_WAIT_RANGE. If
                        set to 0, there is no range and every check will be
                        initially scheduled after 2 seconds (which can produce
                        some load). Default: 10
  --act-as-sender       Act only as a sender. Take input from stdin and send
                        it to server(s). Default: False
  --server=SERVER       The address of one or more massive-passive-servers
                        (comma separated). This option is only valid with the
                        --act-as-sender option. Default: none
  --ssl-key=SSL_KEY     The path to the client ssl key file. Default: /etc
                        /massive-passive/massive-passive-client-ssl.key
  --ssl-cert=SSL_CERT   The path to the client ssl cert file. Default: /etc
                        /massive-passive/massive-passive-client-ssl.cert
  --ssl-ca-cert=SSL_CA_CERT
                        The path to the ssl ca cert file. Default: /etc
                        /massive-passive/massive-passive-ssl-ca.cert

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
    * implement a thread which uses pyinotify to monitor the ALLOWED_CLIENT_CERT_DIR
      in "realtime" and apply changes (add/remove events) instantly.
    * Make it possible that the massive-passive client can configure it's checks
      on it's own - based on the nagios/icinga config. This feature can be switched of.



