from dataclasses import dataclass

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
    fk_references: list[Reference]
    pk_references: list[Reference]

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