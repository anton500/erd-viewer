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

@dataclass
class Tables:
    """Class is a list of all tables."""
    tables: dict[str, Table] = field(default_factory=dict)

    def add_table(self, name: str, table: Table) -> None:
        self.tables[name] = table

def is_new_table(prev_schema, prev_table, cur_schema, cur_table) -> bool:
    if prev_schema and prev_table and (prev_schema != cur_schema or prev_table != cur_table):
        return True
    return False

def read_data_from_csv(csv_path: Path) -> None:

    tables = Tables()
    t = Table()

    with open(csv_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        prev_schema = None
        prev_table = None

        for row in reader:
            cur_schema = row['TABLE_SCHEMA']
            cur_table = row['TABLE_NAME']
            col = Column(name=row['COLUMN_NAME'], data_type=row['DATA_TYPE'], nullable=row['IS_NULLABLE'])

            if is_new_table(prev_schema, prev_table, cur_schema, cur_table):
                t.schema = prev_schema
                t.name = prev_table
                tables.add_table(name='.'.join([t.schema, t.name]), table=t)
                t = Table()

            t.add_column(col)

            prev_schema = cur_schema
            prev_table = cur_table

    print(tables.tables['dlfe.TasksUpdate'])

if __name__ == '__main__':
    read_data_from_csv(Path('ddl.csv'))