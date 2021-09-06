import json
import configparser
from pathlib import Path

from erd_viewer.database import Database, Table, Schema, Column, Reference 

class Config():

    __FILENAME = 'config.ini'

    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.__read_config(Path(self.__FILENAME))

    def __read_config(self, config_path: Path) -> None:
        with open(config_path) as f:
            self.config.read(f, encoding='utf-8')


class Loader():

    def __init__(self) -> None:
        self.config = Config()
        self.db = self.__deserialize_json(
            self.__read_json(
                Path(self.config.config['dbschema']['folder']) / Path(self.config.config['dbschema']['filename'])
            )   
        )

    def __read_json(self, json_path: Path):
        with open(json_path) as j:
            return j.read()

    def __deserialize_json(self, json_str: str) -> Database:
        json_list = json.loads(json_str)
        db = Database()    
        for schema in json_list:
            schema_name = schema['name']
            db.add_schema(schema_name, Schema(schema_name))
            for table in schema['tables']:
                table_name = table['name']
                db.schemas[schema_name].add_table(table_name, Table(table_name))
                for column in table['columns']:
                    column_name = column['name']
                    db.schemas[schema_name].tables[table_name].add_column(
                        column_name,
                        Column(
                            name=column_name,
                            type=column['type'],
                            null=column['null']
                        )
                    )

                    if 'fk_references' in column:
                        for fk_ref in column['fk_references']:
                            db.schemas[schema_name].tables[table_name].columns[column_name].add_fk_reference(
                                Reference(
                                    schema=fk_ref['schema'], 
                                    table=fk_ref['table'], 
                                    column=fk_ref['column']
                                )
                            )
                    if 'pk_references' in column:
                        for pk_ref in column['pk_references']:
                            db.schemas[schema_name].tables[table_name].columns[column_name].add_pk_reference(
                                Reference(
                                    schema=pk_ref['schema'], 
                                    table=pk_ref['table'], 
                                    column=pk_ref['column']
                                )
                            )
        return db