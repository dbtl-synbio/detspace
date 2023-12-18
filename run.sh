#!/bin/bash
DETSPACE_DATA=$HOME/03.DetSpace
SECRET_KEY=`echo $RANDOM | md5sum | head -c 20`

killall gunicorn
gunicorn -c config/gunicorn/dev.py
