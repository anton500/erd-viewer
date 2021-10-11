#!/bin/sh

nginx
redis-server /etc/redis.conf

if python -m erd_viewer.loader.load_data; then
    uwsgi uwsgi.ini
fi
