import json
from collections import namedtuple

from graphviz import Digraph

from erd_viewer.database import Database, Table, Column, Reference
from erd_viewer.loader.redis import RedisClient
from erd_viewer.loader.loader import DBJSONDecoder

class Dot:

    __HTML_TABLE_TEMPLATE = '<<table>{thead}{tbody}</table>>'
    __HTML_TABLE_HEAD_TEMPLATE = '<tr><td colspan="2">{thead}</td></tr>'
    __HTML_TABLE_BODY_TEMPLATE = '{tbody}'
    __HTML_TABLE_ROW_TEMPLATE = '<tr><td port="{port}">{name}</td><td>{datatype}</td></tr>'

    def __get_html_table(self, schema_name: str, table: Table) -> str:
        thead = self.__HTML_TABLE_HEAD_TEMPLATE.format(thead='.'.join([schema_name, table.name]))
        tbody = ''
        for column in table.columns:
            tbody += self.__HTML_TABLE_ROW_TEMPLATE.format(port=column.name, name=column.name, datatype=column.type)

        tbody = self.__HTML_TABLE_BODY_TEMPLATE.format(tbody=tbody)
        return self.__HTML_TABLE_TEMPLATE.format(thead=thead, tbody=tbody)

    def render_digraph(self, graph: Digraph) ->bytes:
        return graph.pipe(format='svg')

    # def get_digraph(self, **kwargs) -> Digraph:
    #     digraph = Digraph(**kwargs)

    #     for schema in self.database.schemas:
    #         for table in schema.tables:
    #             digraph.node(
    #                 '.'.join([schema.name, table.name]),
    #                 label=self.__get_html_table(schema_name=schema.name, table=table)
    #             )
    #             for column in table.columns:
    #                 for fk_ref in column.fk_references:
    #                     digraph.edge(
    #                         ':'.join(['.'.join([schema.name, table.name]), column.name]),
    #                         ':'.join(['.'.join([fk_ref.schema, fk_ref.table]), fk_ref.column])
    #                     )

    #     return digraph

class RelatedTables(Dot):

    def __init__(self, schema_name: str, table_name: str, depth: int, onlykeys=bool) -> None:
        self.redis = RedisClient().get_client()
        self.unvisited = {(schema_name, table_name)}
        self.tables = self.__get_related_tables(self.unvisited, depth)
        return None

    def __get_related_tables(self, unvisited: set, depth: int, visited: set = None) -> set:
        if visited is None:
            visited = set()

        if depth == 0:
            return visited.union(unvisited)

        for schema_name, table_name in unvisited.copy():
            visited.add((schema_name, table_name))
            unvisited.remove((schema_name, table_name))
            for column in self.__get_columns(schema_name, table_name):
                for fk_ref in column.fk_references:
                    if (fk_ref.schema, fk_ref.table) not in visited:
                        unvisited.add((fk_ref.schema, fk_ref.table))
                for pk_ref in column.fk_references:
                    if (pk_ref.schema, pk_ref.table) not in visited:
                        unvisited.add((pk_ref.schema, pk_ref.table))
        return self.__get_related_tables(unvisited, depth-1, visited)

    def __get_columns(self, schema_name: str, table_name: str) -> list:
        json_table = self.redis.hget(schema_name, table_name)
        return json.loads(json_table, cls=DBJSONDecoder)