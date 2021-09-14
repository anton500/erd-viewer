import json
from typing import Union
from dataclasses import asdict

from erd_viewer.loader.config import config
from erd_viewer.loader.redis import RedisClient
from erd_viewer.database import Database, Table, Schema, Column, Reference 

class DBJSONDecoder(json.JSONDecoder):

    def __init__(self) -> None:
        super().__init__(object_hook=self.__object_decoder)

    def __object_decoder(self, obj: dict) -> Union[Schema, Table, Column, Reference, dict]:
        if set(Schema.__annotations__.keys()).issubset(obj.keys()): # pylint: disable=no-member
            return Schema(name=obj['name'], tables=obj['tables'])
        elif set(Table.__annotations__.keys()).issubset(obj.keys()): # pylint: disable=no-member
            return Table(name=obj['name'], columns=obj['columns'])
        elif set(list(Column.__annotations__.keys())[:3]).issubset(obj.keys()): # pylint: disable=no-member
            return Column(
                name=obj['name'], 
                type=obj['type'],
                null=obj['null'],
                fk_references=obj.get('fk_references', []),
                pk_references=obj.get('pk_references', [])
            )
        elif set(Reference.__annotations__.keys()).issubset(obj.keys()): # pylint: disable=no-member
            return Reference(schema=obj['schema'], table=obj['table'], column=obj['column'])
        else:
            return obj

class Loader():

    def __init__(self) -> None:
        self.db = self.__deserialize_json(self.__read_json(config.get('dbschema', 'filename')))
        self.redis = RedisClient().get_client()
        self.__put_db_into_redis()
        return None

    def __read_json(self, json_path: str) -> str:
        with open(json_path) as j:
            return j.read()

    def __deserialize_json(self, json_str: str) -> Database:
        return Database(schemas=json.loads(json_str, cls=DBJSONDecoder))
    
    def __put_db_into_redis(self) -> None:
        for schema in self.db.schemas:
            for table in schema.tables:
                self.redis.hset(schema.name, table.name, json.dumps([asdict(column) for column in table.columns]))
        return None