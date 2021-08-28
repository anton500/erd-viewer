import csv
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field

from graphviz import Digraph

@dataclass
class Column:
    """Class describes column of table in database"""
    name: str
    type: str
    null: str
    key: str

@dataclass
class Table:
    """Class represents table in database."""
    name: str
    columns: dict[str, Column] = field(default_factory=dict)

    def add_column(self, name: str, column: Column) -> None:
        self.columns[name] = column

@dataclass
class Schema:
    """Class represents schema in database."""
    name: str
    tables: dict[str, Table] = field(default_factory=dict)

    def add_table(self, name: str, table: Table) -> None:
        self.tables[name] = table

@dataclass
class Reference:
    """Class represents reference between two tables"""

    fk_schema: str
    fk_table: str
    fk_column: str
    key_schema: str
    key_table: str
    key_column: str

class Dot:

    __HTML_TABLE_TEMPLATE = '<<table>{thead}{tbody}</table>>'
    __HTML_TABLE_HEAD_TEMPLATE = '<tr><td colspan="2">{thead}</td></tr>'
    __HTML_TABLE_BODY_TEMPLATE = '{tbody}'
    __HTML_TABLE_ROW_TEMPLATE = '<tr><td port="{port}">{name}</td><td>{datatype}</td></tr>'

    def __init__(self) -> None:
        self.schemas: dict[str, Schema] = {}
        self.references: list[Reference] = []

    def add_schema(self, name: str, schema: Schema) -> None:
        self.schemas[name] = schema

    def add_reference(self, reference: Reference) -> None:
        self.references.append(reference)

    def __get_html_table(self, schema_name: str, table: Table) -> str:
        thead = self.__HTML_TABLE_HEAD_TEMPLATE.format(thead='.'.join([schema_name, table.name]))
        tbody = ''
        for column in table.columns.values():
            tbody += self.__HTML_TABLE_ROW_TEMPLATE.format(port=column.name, name=column.name, datatype=column.type)

        tbody = self.__HTML_TABLE_BODY_TEMPLATE.format(tbody=tbody)
        return self.__HTML_TABLE_TEMPLATE.format(thead=thead, tbody=tbody)

    def get_dot(self, **kwargs) -> Digraph:
        dot = Digraph(**kwargs)

        for schema in self.schemas.values():
            for table in schema.tables.values():
                dot.node(
                    '.'.join([schema.name, table.name]),
                    label=self.__get_html_table(schema_name=schema.name, table=table)
                    )

        for ref in self.references:
            dot.edge(
                ':'.join([ref.key_table, ref.key_column]),
                ':'.join([ref.fk_table, ref.fk_column])
                )

        return dot

def read_data_from_csv(tables_csv_path: Path, references_csv_path: Path) -> None:

    dot = Dot()

    with open(tables_csv_path) as csvfile:
        reader = csv.DictReader(f=csvfile, delimiter=';')
        for row in reader:
            schema_name = row['schema']
            table_name = row['table']
            column_name = row['column']
            column_type = row['column_type']

            if schema_name not in dot.schemas:
                dot.add_schema(schema_name, Schema(name=schema_name))

            if table_name not in dot.schemas[schema_name].tables:
                dot.schemas[schema_name].add_table(
                    name=table_name,
                    table=Table(name=table_name)
                    )

            dot.schemas[schema_name].tables[table_name].add_column(
                name=column_name,
                column=Column(
                    name=column_name,
                    type=column_type,
                    null='',
                    key=''
                    )
                )

    with open(references_csv_path) as csvfile:
        reader = csv.DictReader(f=csvfile, delimiter=';')
        for row in reader:
            table_name = '.'.join([row['parent_schema'], row['parent_table']])
            table_column = row['parent_column']
            ref_table_name = '.'.join([row['referenced_schema'], row['referenced_table']])
            ref_table_column = row['referenced_column']

            dot.add_reference(
                Reference(
                    fk_schema='',
                    fk_table=ref_table_name,
                    fk_column=ref_table_column,
                    key_schema='',
                    key_table=table_name,
                    key_column=table_column
                    )
                )

        dot.get_dot(filename='dot.dot', directory=Path('dot/'), node_attr={'shape': 'plaintext'}).save()

    return None

def deserialize_json_tables_into_dot(json_obj: list, dot: Dot) -> None:
    for schema in json_obj:
        schema_name = schema['name']
        dot.add_schema(schema_name, Schema(schema_name))
        for table in schema['tables']:
            table_name = table['name']
            dot.schemas[schema_name].add_table(table_name, Table(table_name))
            for column in table['columns']:
                dot.schemas[schema_name].tables[table_name].add_column(
                    column['name'],
                    Column(
                        name=column['name'],
                        type=column['type'],
                        null=column['null'],
                        key=column['key'])
                    )
    return

def deserialize_json_refs_into_dot(json_obj: list, dot: Dot) -> None:
    for ref in json_obj:
        dot.add_reference(
            Reference(
                fk_schema=ref['fk_schema'],
                fk_table=ref['fk_table'],
                fk_column=ref['fk_column'],
                key_schema=ref['key_schema'],
                key_table=ref['key_table'],
                key_column=ref['key_column']
            )
        )

    return

def read_data_from_json(tables_json_path: Path, references_json_path: Path, dot: Dot) -> None:
    with open(tables_json_path) as j:
        json_tables_obj = json.loads(j.read())

    with open(references_json_path) as j:
        json_ref_obj = json.loads(j.read())

    deserialize_json_tables_into_dot(json_tables_obj, dot)
    deserialize_json_refs_into_dot(json_ref_obj, dot)

    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create DOT file for Graphviz render from db structure and references.')
    parser.add_argument(
        '-t',
        '--tables',
        dest='tab',
        help='file containing db tables',
        required=True,
        type=Path
        )
    parser.add_argument(
        '-r',
        '--references',
        dest='ref',
        help='file containing references between tables',
        required=True,
        type=Path
        )
    parser.add_argument(
        '-o',
        '--output',
        dest='out',
        help='output dot file',
        required=True,
        type=Path
        )
    parser.add_argument('-S', '--schema', dest='schema', help='process only selected schema')
    parser.add_argument('-T', '--table', dest='table', help='process only selected tables')
    args = parser.parse_args()

    dot = Dot()

    read_data_from_json(tables_json_path=Path(args.tab), references_json_path=Path(args.ref), dot=dot)

    dot.get_dot(filename=args.out, node_attr={'shape': 'plaintext'}).save()
    #read_data_from_csv(Path('data/ddl.csv'), Path('data/references.csv'))