#!/bin/sh

if python -m erd_viewer.loader.load_data; then
    uwsgi uwsgi.ini
fi
