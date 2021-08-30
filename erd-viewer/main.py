import json
import argparse
import uuid
from pathlib import Path
from dataclasses import dataclass, field

from graphviz import Digraph

@dataclass
class Reference:
    schema: str
    table: str
    column: str

@dataclass
class Column:
    name: str
    type: str
    null: str
    fk_references: list[Reference] = field(default_factory=list)
    pk_references: list[Reference] = field(default_factory=list)

    def add_fk_reference(self, reference: Reference) -> None:
        return self.fk_references.append(reference)

    def add_pk_reference(self, reference: Reference) -> None:
        return self.pk_references.append(reference)

@dataclass
class Table:
    name: str
    columns: dict[str, Column] = field(default_factory=dict)

    def add_column(self, name: str, column: Column) -> None:
        self.columns[name] = column

@dataclass
class Schema:
    name: str
    tables: dict[str, Table] = field(default_factory=dict)

    def add_table(self, name: str, table: Table) -> None:
        self.tables[name] = table

@dataclass
class Database:
    schemas: dict[str, Schema] = field(default_factory=dict)

    def add_schema(self, name: str, schema: Schema) -> None:
        self.schemas[name] = schema

class Dot:

    __HTML_TABLE_TEMPLATE = '<<table>{thead}{tbody}</table>>'
    __HTML_TABLE_HEAD_TEMPLATE = '<tr><td colspan="2">{thead}</td></tr>'
    __HTML_TABLE_BODY_TEMPLATE = '{tbody}'
    __HTML_TABLE_ROW_TEMPLATE = '<tr><td port="{port}">{name}</td><td>{datatype}</td></tr>'

    def __init__(self, database: Database) -> None:
        self.database = database

    def __get_html_table(self, schema_name: str, table: Table) -> str:
        thead = self.__HTML_TABLE_HEAD_TEMPLATE.format(thead='.'.join([schema_name, table.name]))
        tbody = ''
        for column in table.columns.values():
            tbody += self.__HTML_TABLE_ROW_TEMPLATE.format(port=column.name, name=column.name, datatype=column.type)

        tbody = self.__HTML_TABLE_BODY_TEMPLATE.format(tbody=tbody)
        return self.__HTML_TABLE_TEMPLATE.format(thead=thead, tbody=tbody)

    def get_digraph(self, **kwargs) -> Digraph:
        digraph = Digraph(**kwargs)

        for schema in self.database.schemas.values():
            for table in schema.tables.values():
                digraph.node(
                    '.'.join([schema.name, table.name]),
                    label=self.__get_html_table(schema_name=schema.name, table=table)
                )
                for column in table.columns.values():
                    for fk_ref in column.fk_references:
                        digraph.edge(
                            ':'.join(['.'.join([schema.name, table.name]), column.name]),
                            ':'.join(['.'.join([fk_ref.schema, fk_ref.table]), fk_ref.column])
                        )

        return digraph

def deserialize_json(json_str: str) -> Database:
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
                            Reference(schema=fk_ref['schema'], table=fk_ref['table'], column=fk_ref['column'])
                        )
                if 'pk_references' in column:
                    for pk_ref in column['pk_references']:
                        db.schemas[schema_name].tables[table_name].columns[column_name].add_pk_reference(
                            Reference(schema=pk_ref['schema'], table=pk_ref['table'], column=pk_ref['column'])
                        )
    return db

def read_json(json_path: Path) -> str:
    with open(json_path) as j:
        return j.read()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Create DOT file for Graphviz render from db schema.')
    parser.add_argument('-f', '--file', dest='file', help='json file containing db schema', required=True, type=Path)
    parser.add_argument('-n', '--name', dest='name', help='graph name', type=str)
    #parser.add_argument('-o', '--output', dest='output', help='output dot file', required=True, type=Path)
    #parser.add_argument('-r', '--render', dest='render', help='output rendered file', type=Path)
    parser.add_argument('-s', '--schema', dest='schema', help='process only selected schema')
    parser.add_argument('-t', '--table', dest='table', help='process only selected tables')
    parser.add_argument('--no-render', dest='norender', help='only save, don\'t render')

    return parser.parse_args()

def main(args) -> str:
    json_str = read_json(Path(args.file))
    database = deserialize_json(json_str)
    dot = Dot(database)
    digraph = dot.get_digraph(
        name=args.name if args.name else str(uuid.uuid4()),
        engine='neato',
        format='svg',
        graph_attr={'splines': 'spline', 'overlap': 'prism'}, 
        node_attr={'shape': 'plaintext'}
    )

    if args.norender is None:
        return digraph.render(directory=Path('graphs/'))
    return digraph.save(directory=Path('graphs/'))
     
if __name__ == '__main__':
    main(parse_args())