FROM redis:6-alpine

COPY docker-compose/redis/redis.conf /usr/local/etc/redis/redis.conf
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
