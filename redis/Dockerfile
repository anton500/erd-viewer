FROM redis:6-alpine

COPY redis/redis.conf /usr/local/etc/redis/redis.conf
RUN mkdir /tmp/redis && chown redis:redis /tmp/redis
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
