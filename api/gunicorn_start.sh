#!/bin/sh
WORKERS=${1:-4}
gunicorn -b 0.0.0.0:8000 -w $WORKERS 'api.app:config_app()'
