FROM python:3.9-slim AS uwsgi_builder

RUN apt-get -qq update \
    && apt-get -qq install build-essential python-dev libpcre3-dev -y \
    && pip install --no-cache-dir "uwsgi>=2.0.19,<2.1"

FROM python:3.9-slim

WORKDIR /usr/erd-viewer
COPY requirements.txt .

RUN apt-get -qq update \
    && apt-get -qq install graphviz libpcre3 -y \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uwsgi_builder /usr/local/bin/uwsgi /usr/local/bin/uwsgi

COPY uwsgi/uwsgi.ini .
COPY erd_viewer/ erd_viewer/

EXPOSE 3031/tcp

COPY docker-entrypoint.sh .
RUN chmod 755 docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
