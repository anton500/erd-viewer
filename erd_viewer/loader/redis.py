import redis

from erd_viewer.loader.config import config


class RedisClient:

    con_pool = redis.ConnectionPool().from_url("unix://@/tmp/redis/redis.sock?db=0")

    r = redis.Redis(connection_pool=con_pool)
    r.close()

    def get_client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self.con_pool)
