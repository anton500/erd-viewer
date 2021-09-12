import redis

from erd_viewer.loader.config import config

class RedisClient():

    con_pool = redis.ConnectionPool(
        host=config.get('redis', 'host'), 
        port=config.getint('redis', 'port'), 
        db=config.getint('redis', 'db')
    )

    def __init__(self) -> None:
        self.r = redis.Redis(connection_pool=self.con_pool)
        self.r.config_set('appendonly', config.get('redis-persistance', 'appendonly', fallback='no'))
        self.r.config_set('save', config.get('redis-persistance', 'save', fallback=''))
        return None