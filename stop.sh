#!/bin/bash

# Replace these three settings.
PROJDIR="/repos/workspace/joyotime/stargazer"
PIDFILE="$PROJDIR/logs/fcgi.pid"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    sudo kill `cat -- $PIDFILE`
    sudo rm -f -- $PIDFILE
fi