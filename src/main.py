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
    nullable: str

@dataclass
class Table:
    """Class represents table in database."""
    table_name: str
    columns: list[Column] = field(default_factory=list)

    def add_column(self, column: Column) -> None:
        return self.columns.append(column)

@dataclass
class Reference:
    """Class represents reference between two tables"""
    table_name: str
    column_name: str
    referenced_table_name: str
    referenced_column_name: str

class Dot:

    HTML_TABLE_TEMPLATE = '<<table>{thead}{tbody}</table>>'
    HTML_TABLE_HEAD_TEMPLATE = '<tr><td colspan="2">{thead}</td></tr>'
    HTML_TABLE_BODY_TEMPLATE = '<tbody>{tbody}</tbody>'
    HTML_TABLE_ROW_TEMPLATE = '<tr><td port="{port}">{name}</td><td>{datatype}</td></tr>'
    
    def __init__(self) -> None:
        self.tables: dict[str, Table] = {}
        self.references: dict[str, Reference] = {}

    def __getitem__(self, table_name: str) -> Table:
        return self.tables[table_name]

    def add_table(self, table_name: str, table: Table) -> None:
        self.tables[table_name] = table

    def add_reference(self, ref_name: str, reference: Reference) -> None:
        self.references[ref_name] = reference

    def __get_html_table(self, table: Table) -> str:
        thead = self.HTML_TABLE_HEAD_TEMPLATE.format(thead=table.table_name)
        tbody = ''
        for column in table.columns:
            tbody += self.HTML_TABLE_ROW_TEMPLATE.format(port=column.name, name=column.name, datatype=column.data_type)
        
        return self.HTML_TABLE_TEMPLATE.format(thead=thead, tbody=tbody)
        
    def get_dot(self, **kwargs) -> Digraph:
        dot = Digraph(**kwargs)

        for name, table in self.tables.items():
            dot.node(name, label=self.__get_html_table(table))

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
            table_name = '.'.join([row['schema'], row['table']])

            if table_name not in dot.tables:
                dot.add_table(table_name, Table(table_name=table_name))

            dot[table_name].add_column(
                Column(
                    name=row['column'], 
                    data_type=row['column_type'], 
                    nullable=''
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

    for engine in ['dot', 'neato', 'twopi', 'fdp', 'osage', 'patchwork', 'sfdp']:
        print(engine)
        dot.get_dot(filename=f'{engine}_ortho_false', engine=engine, format='svg', graph_attr={'splines': 'ortho', 'overlap': 'false'}, node_attr={'shape': 'plaintext'}).render(view=True)
        dot.get_dot(filename=f'{engine}_ortho_prism', engine=engine, format='svg', graph_attr={'splines': 'ortho', 'overlap': 'prism'}, node_attr={'shape': 'plaintext'}).render(view=True)
        dot.get_dot(filename=f'{engine}_ortho_true', engine=engine, format='svg', graph_attr={'splines': 'ortho', 'overlap': 'true'}, node_attr={'shape': 'plaintext'}).render(view=True)
        dot.get_dot(filename=f'{engine}', engine=engine, format='svg', node_attr={'shape': 'plaintext'}).render(view=False)

    return None

if __name__ == '__main__':
    read_data_from_csv(Path('ddl.csv'), Path('references.csv'))