import csv
from os import read
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Column:
    """Class describes column of table in database"""
    name: str = None
    data_type: str = None
    nullable: str = None

@dataclass
class Table:
    """Class represents table in database."""
    schema: str = None
    name: str = None
    columns: list[Column] = field(default_factory=list)

    def add_column(self, column: Column) -> None:
        return self.columns.append(column)

@dataclass
class Reference:
    """Class represents reference between two tables"""
    table_name: str = None
    column_name : str = None
    referenced_table_name: str = None
    referenced_column_name: str = None

class Dot:
    def __init__(self) -> None:
        self.tables: dict[str, Table] = {}
        self.references: dict[str, Reference] = {}

    def __getitem__(self, table_name: str) -> Table:
        return self.tables[table_name]

    def add_table(self, table_name: str, table: Table) -> None:
        self.tables[table_name] = table

    def add_reference(self, ref_name: str, reference: Reference) -> None:
        self.references[ref_name] = reference

def read_data_from_csv(tables_csv_path: Path, references_csv_path: Path) -> None:

    dot = Dot()

    with open(tables_csv_path) as csvfile:
        reader = csv.DictReader(f=csvfile, delimiter=';')
        for row in reader:
            table_name = '.'.join([row['TABLE_SCHEMA'], row['TABLE_NAME']])

            if table_name not in dot.tables:
                dot.add_table(table_name, Table(name=table_name))

            dot[table_name].add_column(
                Column(
                    name=row['COLUMN_NAME'], 
                    data_type=row['DATA_TYPE'], 
                    nullable=row['IS_NULLABLE']
                    )
                )

    with open(references_csv_path) as csvfile:
        reader = csv.DictReader(f=csvfile, delimiter=';')
        for row in reader:
            table_name = '.'.join([row['FK schema'], row['FK table']])
            table_column = row['FK column']
            ref_table_name = '.'.join([row['Referenced schema'], row['Referenced table']])
            ref_table_column = row['Referenced column']

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


    print(dot.tables['dlfe.TasksUpdate'])
    print(dot.references['dlfe.LeaseContracts.ProjectID->dlfe.Projects.ProjectID'])

if __name__ == '__main__':
    read_data_from_csv(Path('ddl.csv'), Path('references.csv'))