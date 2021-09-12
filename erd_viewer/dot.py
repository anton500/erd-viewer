from graphviz import Digraph

from erd_viewer.database import Database, Table

class Dot:

    __HTML_TABLE_TEMPLATE = '<<table>{thead}{tbody}</table>>'
    __HTML_TABLE_HEAD_TEMPLATE = '<tr><td colspan="2">{thead}</td></tr>'
    __HTML_TABLE_BODY_TEMPLATE = '{tbody}'
    __HTML_TABLE_ROW_TEMPLATE = '<tr><td port="{port}">{name}</td><td>{datatype}</td></tr>'

    def __init__(self, database: Database) -> None:
        self.database = database

    def __get_html_table(self, schema_name: str, table: Table) -> str:
        thead = self.__HTML_TABLE_HEAD_TEMPLATE.format(thead='.'.join([schema_name, table.name]))
        tbody = ''
        for column in table.columns:
            tbody += self.__HTML_TABLE_ROW_TEMPLATE.format(port=column.name, name=column.name, datatype=column.type)

        tbody = self.__HTML_TABLE_BODY_TEMPLATE.format(tbody=tbody)
        return self.__HTML_TABLE_TEMPLATE.format(thead=thead, tbody=tbody)

    def get_digraph(self, **kwargs) -> Digraph:
        digraph = Digraph(**kwargs)

        for schema in self.database.schemas:
            for table in schema.tables:
                digraph.node(
                    '.'.join([schema.name, table.name]),
                    label=self.__get_html_table(schema_name=schema.name, table=table)
                )
                for column in table.columns:
                    for fk_ref in column.fk_references:
                        digraph.edge(
                            ':'.join(['.'.join([schema.name, table.name]), column.name]),
                            ':'.join(['.'.join([fk_ref.schema, fk_ref.table]), fk_ref.column])
                        )

        return digraph