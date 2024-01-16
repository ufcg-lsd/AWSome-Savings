#!/bin/bash

command -v mpstat >/dev/null 2>&1 || { echo >&2 "I require mpstat, but it's not installed.  Please install it using sudo apt-get install sysstat."; exit 1; }

export LC_ALL="C"
TIME_BETWEEN_COMMANDS=1
echo TIMESTAMP, USER, NICE, SYS, IOWAIT, IRQ, SOFT, STEAL, GUEST, GNICE, IDLE
while [ -e /proc/$1 ]; do
    /usr/bin/mpstat $TIME_BETWEEN_COMMANDS 1 | grep -e '[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}[ \t]*'all | awk -v date="$( date +"%s" )" '{ print date", "$3", "$4", "$5", "$6", "$7", "$8", "$9", "$10", "$11", "$12 }' 2> /dev/null
done
