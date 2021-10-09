from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaTable:
    schema: str
    table: str


@dataclass(frozen=True)
class SchemaTableColumn:
    schema: str
    table: str
    column: str


@dataclass
class Column:
    name: str
    type: str
    null: str
    fk_references: list[SchemaTableColumn]
    pk_references: list[SchemaTableColumn]


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
