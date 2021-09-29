import json
from typing import Union
from dataclasses import asdict

from erd_viewer.loader.config import config
from erd_viewer.loader.redis import RedisClient
from erd_viewer.database import Database, Table, Schema, Column, SchemaTableColumn

class DBJSONDecoder(json.JSONDecoder):

    def __init__(self) -> None:
        super().__init__(object_hook=self._object_decoder)

    def _object_decoder(self, obj: dict) -> Union[Schema, Table, Column, SchemaTableColumn, dict]:
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
        elif set(SchemaTableColumn.__annotations__.keys()).issubset(obj.keys()): # pylint: disable=no-member
            return SchemaTableColumn(schema=obj['schema'], table=obj['table'], column=obj['column'])
        else:
            return obj

class Loader():

    def __init__(self) -> None:
        self.db = self._deserialize_json(self._read_json(config.get('dbschema', 'filename')))
        self.redis = RedisClient().get_client()
        self._put_db_into_redis()
        return None

    def _read_json(self, json_path: str) -> str:
        with open(json_path) as j:
            return j.read()

    def _deserialize_json(self, json_str: str) -> Database:
        return Database(schemas=json.loads(json_str, cls=DBJSONDecoder))

    def _put_db_into_redis(self) -> None:
        for schema in self.db.schemas:
            self.redis.rpush('schemas:list', schema.name)
            for table in schema.tables:
                self.redis.hset(schema.name, table.name, json.dumps([asdict(column) for column in table.columns]))
        return None