from dataclasses import dataclass

@dataclass(frozen=True)
class ColumnWithPath:
    schema: str
    table: str
    column: str

@dataclass
class Column:
    name: str
    type: str
    null: str
    fk_references: list[ColumnWithPath]
    pk_references: list[ColumnWithPath]

@dataclass
class Table:
    name: str
    columns: list[Column]

@dataclass
class Schema:
    name: str
    tables: list[Table]

@dataclass
class Database:
    schemas: list[Schema]