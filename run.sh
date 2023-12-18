#!/bin/bash

killall gunicorn
gunicorn -c config/gunicorn/dev.py
