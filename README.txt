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
several other every 30 seconds, and so on.

You can also just use every existing normal nagios/icinga host and service
check (if written with the standard rules for nagios/icinga checks in mind)
and execute it via massive-passive. The result of a check will be translated
in the correct nsca format and send to (maybe multiple) nagios/icinga hosts.
And if you want, this will be done in batch mode. So you could send 5 results
in one nsca connection.


How?
----

Get the source from github (https://github.com/mysportgroup/massive-passive).
Make sure you have python and python setuptools installed.
Do:
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
    "command": "/bin/bash -c '/bin/echo hello this is an environment test: $TESTERTEST'",
    "env": {"TESTERTEST": "moep!"},
    "check_type": "service_check",
    "check_hostname": "this.is.a.hostname"
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


After configuring your first check, you can do:
    kill -1 <PID OF MASSIVE-PASSIVE> 

    or

    /etc/init.d/massive-passive reload

    or (on debian)
    
    service massive-passive reload
to reload the configs at runtime. 

A brief documentation will follow. Thank you and have fun!

