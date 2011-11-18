#!/bin/bash

# Replace these three settings.
PROJDIR="/repos/workspace/joyotime/stargazer"
PIDFILE="$PROJDIR/logs/fcgi.pid"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

sudo ./manage.py runfcgi pidfile=$PIDFILE host=127.0.0.1 port=3033