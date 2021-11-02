import os
import redis


class RedisClient:

    _REDIS_DB = "0"

    _REDIS_HOST = os.getenv("REDIS_HOST")
    _REDIS_PORT = os.getenv("REDIS_PORT", "6379")

    _REDIS_SOCKET = "/var/run/redis/redis.sock"

    if _REDIS_HOST:
        _con_str = f"redis://{_REDIS_HOST}:{_REDIS_PORT}/{_REDIS_DB}"
    else:
        _con_str = f"unix://{_REDIS_SOCKET}?db={_REDIS_DB}"
    _con_pool = redis.ConnectionPool().from_url(_con_str)

    def get_client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self._con_pool)
