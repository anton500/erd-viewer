import csv
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

class Dot:
    def __init__(self) -> None:
        self.tables = {}

    def __getitem__(self, table_name: str) -> Table:
        return self.tables[table_name]

    def add_table(self, table_name: str, table: Table) -> None:
        self.tables[table_name] = table

def read_data_from_csv(csv_path: Path) -> None:

    dot = Dot()

    with open(csv_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            table_name = '.'.join([row['TABLE_SCHEMA'], row['TABLE_NAME']])

            if table_name not in dot.tables:
                dot.add_table(table_name, Table(name=table_name))

            dot[table_name].add_column(Column(name=row['COLUMN_NAME'], data_type=row['DATA_TYPE'], nullable=row['IS_NULLABLE']))

    print(dot.tables['dlfe.TasksUpdate'])

if __name__ == '__main__':
    read_data_from_csv(Path('ddl.csv'))