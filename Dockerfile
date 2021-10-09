FROM python:3.9-slim

WORKDIR /usr/erd-viewer
COPY requirements.txt .

RUN apt-get -qq update && apt-get -qq install graphviz build-essential python-dev libpcre3 libpcre3-dev -y \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge --auto-remove build-essential python-dev libpcre3-dev -y \
    && rm -rf /var/lib/apt/lists/*

COPY uwsgi/uwsgi.ini .
COPY erd_viewer/ erd_viewer/

EXPOSE 3031/tcp

COPY docker-entrypoint.sh .
RUN chmod 755 docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
