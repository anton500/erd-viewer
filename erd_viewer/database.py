from dataclasses import dataclass, field

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

    # def add_fk_reference(self, reference: Reference) -> None:
    #     return self.fk_references.append(reference)

    # def add_pk_reference(self, reference: Reference) -> None:
    #     return self.pk_references.append(reference)

@dataclass
class Table:
    name: str
    columns: list[Column]

    # def add_column(self, column: Column) -> None:
    #     return self.columns.append(column)

@dataclass
class Schema:
    name: str
    tables: list[Table]

    # def add_table(self, table: Table) -> None:
    #     return self.tables.append(table)

@dataclass
class Database:
    schemas: list[Schema]

    # def add_schema(self, schema: Schema) -> None:
    #     return self.schemas.append(schema)