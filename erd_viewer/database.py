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
        return None

@dataclass
class Schema:
    name: str
    tables: dict[str, Table] = field(default_factory=dict)

    def add_table(self, name: str, table: Table) -> None:
        self.tables[name] = table
        return None

@dataclass
class Database:
    schemas: dict[str, Schema] = field(default_factory=dict)

    def add_schema(self, name: str, schema: Schema) -> None:
        self.schemas[name] = schema
        return None