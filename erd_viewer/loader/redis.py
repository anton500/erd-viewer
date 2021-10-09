import redis

from erd_viewer.loader.config import config


class RedisClient:

    con_pool = redis.ConnectionPool(
        host=config.get("redis", "host"),
        port=config.getint("redis", "port"),
        db=config.getint("redis", "db"),
    )

    r = redis.Redis(connection_pool=con_pool)
    r.config_set(
        "appendonly", config.get("redis-persistance", "appendonly", fallback="no")
    )
    r.config_set("save", config.get("redis-persistance", "save", fallback=""))
    r.close()

    def get_client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self.con_pool)
