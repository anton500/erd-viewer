import csv
from os import read
from pathlib import Path
from dataclasses import dataclass, field

from graphviz import Digraph

@dataclass
class Column:
    """Class describes column of table in database"""
    name: str
    data_type: str
    null: str
    key: str

@dataclass
class Table:
    """Class represents table in database."""
    name: str
    fullname: str
    columns: dict[str, Column] = field(default_factory=dict)

    def add_column(self, column_name: str, column: Column) -> None:
        self.columns[column_name] = column

@dataclass
class Schema:
    """Class represents schema in database."""
    name: str
    tables: dict[str, Table] = field(default_factory=dict)

    def add_table(self, table_name: str, table: Table) -> None:
        self.tables[table_name] = table

@dataclass
class Reference:
    """Class represents reference between two tables"""
    table_name: str
    column_name: str
    referenced_table_name: str
    referenced_column_name: str

class Dot:

    __HTML_TABLE_TEMPLATE = '<<table>{thead}{tbody}</table>>'
    __HTML_TABLE_HEAD_TEMPLATE = '<tr><td colspan="2">{thead}</td></tr>'
    __HTML_TABLE_BODY_TEMPLATE = '{tbody}'
    __HTML_TABLE_ROW_TEMPLATE = '<tr><td port="{port}">{name}</td><td>{datatype}</td></tr>'

    def __init__(self) -> None:
        self.schemas: dict[str, Schema] = {}
        self.references: dict[str, Reference] = {}

    def add_schema(self, schema_name: str, schema: Schema) -> None:
        self.schemas[schema_name] = schema

    def add_reference(self, ref_name: str, reference: Reference) -> None:
        self.references[ref_name] = reference

    def __get_html_table(self, table: Table) -> str:
        thead = self.__HTML_TABLE_HEAD_TEMPLATE.format(thead=table.fullname)
        tbody = ''
        for column in table.columns.values():
            tbody += self.__HTML_TABLE_ROW_TEMPLATE.format(port=column.name, name=column.name, datatype=column.data_type)

        tbody = self.__HTML_TABLE_BODY_TEMPLATE.format(tbody=tbody)
        return self.__HTML_TABLE_TEMPLATE.format(thead=thead, tbody=tbody)

    def get_dot(self, **kwargs) -> Digraph:
        dot = Digraph(**kwargs)

        for schema in self.schemas.values():
            for table in schema.tables.values():
                dot.node(table.fullname, label=self.__get_html_table(table=table))

        for ref in self.references.values():
            dot.edge(
                ':'.join([ref.table_name, ref.column_name]),
                ':'.join([ref.referenced_table_name, ref.referenced_column_name])
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
                    table_name=table_name,
                    table=Table(
                        name=table_name,
                        fullname='.'.join([schema_name, table_name])
                        )
                    )

            dot.schemas[schema_name].tables[table_name].add_column(
                column_name=column_name,
                column=Column(
                    name=column_name,
                    data_type=column_type,
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

            ref_name = f"{'.'.join([table_name, table_column])}->{'.'.join([ref_table_name, ref_table_column])}"
            dot.add_reference(
                ref_name,
                Reference(
                    table_name=table_name,
                    column_name=table_column,
                    referenced_table_name=ref_table_name,
                    referenced_column_name=ref_table_column
                    )
                )

        dot.get_dot(filename='dot.dot', directory=Path('dot/'), node_attr={'shape': 'plaintext'}).save()

    return None

if __name__ == '__main__':
    read_data_from_csv(Path('data/ddl.csv'), Path('data/references.csv'))