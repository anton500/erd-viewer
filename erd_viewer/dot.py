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

    __graph_attr = {'overlap': 'prism', 'splines': 'spline'}
    __node_attr = {'shape': 'plaintext'}

    def __init__(self, graph_name: str = None, engine: str = 'neato',
                 graph_attr: dict = None, node_attr: dict = None, edge_attr: dict = None) -> None:
        self.graph_name = graph_name
        self.engine = engine

        self.graph_attr = graph_attr if graph_attr else self.__graph_attr
        self.node_attr = node_attr if node_attr else self.__node_attr
        self.edge_attr = edge_attr

        self.redis = RedisClient().get_client()
        return None

    def get_columns(self, schema: str, table: str) -> list:
        json_columns = self.redis.hget(schema, table)
        return json.loads(json_columns, cls=DBJSONDecoder)

    def __get_html_table(self, schema: str, table: str, columns: list[Column], onlykeys: bool) -> str:
        thead = self.__HTML_TABLE_HEAD_TEMPLATE.format(thead='.'.join([schema, table]))
        tbody = ''
        for column in columns:
            if (not onlykeys) or (onlykeys and (column.fk_references or column.pk_references)):
                tbody += self.__HTML_TABLE_ROW_TEMPLATE.format(port=column.name, name=column.name, datatype=column.type)

        tbody = self.__HTML_TABLE_BODY_TEMPLATE.format(tbody=tbody)
        return self.__HTML_TABLE_TEMPLATE.format(thead=thead, tbody=tbody)

    def build_digraph(self, tables: set, onlykeys: bool = False) -> Digraph:
        digraph = Digraph(name=self.graph_name, engine=self.engine, graph_attr=self.graph_attr,
                          node_attr=self.node_attr, edge_attr=self.edge_attr)

        for schema, table in tables:
            columns = self.get_columns(schema, table)
            digraph.node(name=f'{schema}.{table}', label=self.__get_html_table(schema, table, columns, onlykeys))
            for column in columns:
                for fk_ref in column.fk_references:
                    if (fk_ref.schema, fk_ref.table) in tables:
                        digraph.edge(
                            tail_name=f'{schema}.{table}:{column.name}',
                            head_name=f'{fk_ref.schema}.{fk_ref.table}:{fk_ref.column}'
                        )

        return digraph

    def render_digraph(self, graph: Digraph) ->bytes:
        return graph.pipe(format='svg')

class RelatedTables(Dot):

    def __init__(
            self, schema_name: str, table_name: str, depth: int, onlykeys: bool = False, graph_name: str = None,
            engine: str = 'neato', graph_attr: dict = None, node_attr: dict = None, edge_attr: dict = None) -> None:
        super().__init__(graph_name, engine, graph_attr, node_attr, edge_attr)
        self.tables = self.__get_related_tables({(schema_name, table_name)}, depth)
        self.onlykeys = onlykeys
        return None

    def __get_related_tables(self, unvisited: set, depth: int, visited: set = None) -> set:
        if visited is None:
            visited = set()

        if depth == 0:
            return visited.union(unvisited)

        for schema_name, table_name in unvisited.copy():
            visited.add((schema_name, table_name))
            unvisited.remove((schema_name, table_name))
            for column in self.get_columns(schema_name, table_name):
                for fk_ref in column.fk_references:
                    if (fk_ref.schema, fk_ref.table) not in visited:
                        unvisited.add((fk_ref.schema, fk_ref.table))
                for pk_ref in column.fk_references:
                    if (pk_ref.schema, pk_ref.table) not in visited:
                        unvisited.add((pk_ref.schema, pk_ref.table))
        return self.__get_related_tables(unvisited, depth-1, visited)

    def get_graph(self) -> bytes:
        digraph = self.build_digraph(self.tables, self.onlykeys)
        return self.render_digraph(digraph)