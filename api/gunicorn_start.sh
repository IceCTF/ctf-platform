#!/bin/sh
gunicorn -b 0.0.0.0:8000 -w $1 'api.app:config_app()'
