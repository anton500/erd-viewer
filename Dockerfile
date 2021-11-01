FROM alpine:3.14 AS graphviz_builder
RUN set -ex \
    && apk add --no-cache msttcorefonts-installer \
    && update-ms-fonts \
    && apk add --no-cache --virtual build_deps \
        build-base \
        glib-dev \
        expat-dev \
        freetype-dev \
        fontconfig-dev \
    && mkdir -p /usr/src \
    && cd /usr/src \
    && wget -O gts.tar.gz "https://sourceforge.net/projects/gts/files/gts/0.7.6/gts-0.7.6.tar.gz" \
    && mkdir /usr/src/gts \
    && tar -xzC /usr/src/gts --strip-components=1 -f gts.tar.gz \
    && rm gts.tar.gz \
    && cd /usr/src/gts \
    && ./configure --prefix=/tmp/gts \
    && make \
    && make install \
    && cp -r /tmp/gts/. /usr/local/ \
    && cd /usr/src \
    && wget -O graphviz.tar.gz "https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/2.49.3/graphviz-2.49.3.tar.gz" \
    && mkdir /usr/src/graphviz \
    && tar -xzC /usr/src/graphviz --strip-components=1 -f graphviz.tar.gz \
    && rm graphviz.tar.gz \
    && cd /usr/src/graphviz \
    && ./configure --prefix=/tmp/graphviz \
    && make \
    && make install \
    && apk del --no-network build_deps \
    && cd / \
    && rm -rf /usr/src \
    && rm -rf /usr/local \
    && rm -rf /tmp/graphviz/{include,share}


FROM python:3.9-alpine3.14 AS uwsgi_builder
RUN set -ex \
    && apk add --no-cache --virtual build_deps \
        build-base \
        linux-headers \
        pcre-dev \
    && pip install --no-cache-dir --prefix=/tmp/uwsgi "uwsgi>=2.0.19,<2.1" \
    && apk del --no-network build_deps


FROM python:3.9-alpine3.14

WORKDIR /usr/erd-viewer
COPY requirements.txt .

RUN apk add --no-cache \
        pcre \
        glib \
        expat \
        freetype \
        fontconfig \
        libstdc++ \
        nginx \
        redis \
    && fc-cache -f \
    && pip install --no-cache-dir -r requirements.txt \
    && rm requirements.txt \
    && adduser -D -H -s /sbin/nologin -G nginx uwsgi \
    && addgroup uwsgi redis \
    && mkdir -p /var/run/uwsgi \
    && chown uwsgi:nginx /var/run/uwsgi \
    && mkdir -p /var/run/redis \
    && chown redis:redis /var/run/redis

COPY --from=graphviz_builder /tmp/graphviz/ /tmp/gts/ /usr/local/
COPY --from=graphviz_builder /usr/share/fonts/truetype/msttcorefonts/ /usr/share/fonts/truetype/msttcorefonts/
COPY --from=uwsgi_builder /tmp/uwsgi /usr/local/

COPY nginx/nginx_uwsgi.conf /etc/nginx/http.d/default.conf
COPY redis/redis.conf /etc/redis.conf
COPY uwsgi/uwsgi.ini uwsgi.ini

COPY data/sample_db_schema.json data/sample_db_schema.json
COPY erd_viewer/ erd_viewer/
COPY web /usr/share/nginx/html

EXPOSE 80/tcp

COPY docker-entrypoint.sh .
RUN chown -R nginx:nginx /usr/share/nginx/html \
    && chmod 755 docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
