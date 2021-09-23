import json

from graphviz import Digraph

from erd_viewer.database import Column, ColumnWithPath
from erd_viewer.loader.redis import RedisClient
from erd_viewer.loader.loader import DBJSONDecoder

class Graph:

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
        if isinstance(json_columns, str):
            return json.loads(json_columns, cls=DBJSONDecoder)
        return []

    def __get_html_table(self, schema: str, table: str, columns: list[Column]) -> str:
        thead = self.__HTML_TABLE_HEAD_TEMPLATE.format(thead='.'.join([schema, table]))
        tbody = ''
        for column in columns:
            tbody += self.__HTML_TABLE_ROW_TEMPLATE.format(port=column.name, name=column.name, datatype=column.type)

        tbody = self.__HTML_TABLE_BODY_TEMPLATE.format(tbody=tbody)
        return self.__HTML_TABLE_TEMPLATE.format(thead=thead, tbody=tbody)

    def __generate_refs(self, tables_with_columns: dict[tuple[str, str], list[Column]],
                        unvisited_tables: set[tuple[str, str]] = None) -> list[tuple[ColumnWithPath, ColumnWithPath]]:

        if unvisited_tables is None:
            unvisited_tables = set()

        refs = []

        for (schema, table), columns in tables_with_columns.items():
            for column in columns:
                if (schema, table) not in unvisited_tables:
                    for fk_ref in column.fk_references:
                        if (fk_ref.schema, fk_ref.table) in tables_with_columns:
                            refs.append((ColumnWithPath(schema, table, column.name), fk_ref))
                else:
                    for fk_ref in column.fk_references:
                        if (fk_ref.schema, fk_ref.table) in set(tables_with_columns).difference(unvisited_tables):
                            refs.append((ColumnWithPath(schema, table, column.name), fk_ref))
        return refs

    def __fill_digraph(self, digraph: Digraph, tables_with_columns: dict[tuple[str, str], list[Column]],
                     refs: list[tuple[ColumnWithPath, ColumnWithPath]]) -> Digraph:

        for (schema, table), columns in tables_with_columns.items():
            digraph.node(name=f'{schema}.{table}', label=self.__get_html_table(schema, table, columns))

        for cwp1, cwp2 in refs:
            digraph.edge(
                tail_name=f'{cwp1.schema}.{cwp1.table}:{cwp1.column}',
                head_name=f'{cwp2.schema}.{cwp2.table}:{cwp2.column}'
            )

        return digraph

    def build_digraph(self, tables: set, onlyrefs: bool = False, unvisited_tables: set = None) -> Digraph:
        digraph = Digraph(name=self.graph_name, engine=self.engine, graph_attr=self.graph_attr,
                          node_attr=self.node_attr, edge_attr=self.edge_attr)

        tables_with_columns = {(schema, table): self.get_columns(schema, table) for schema, table in tables}

        refs = self.__generate_refs(tables_with_columns, unvisited_tables)

        if onlyrefs:
            unique_columns = {cwp for t in refs for cwp in t}

            for (schema, table), columns in tables_with_columns.items():
                filtered_columns = []
                for column in columns:
                    if ColumnWithPath(schema, table, column.name) in unique_columns:
                        filtered_columns.append(column)
                tables_with_columns[(schema, table)] = filtered_columns

        return self.__fill_digraph(digraph, tables_with_columns, refs)

    def render_digraph(self, graph: Digraph) -> str:
        return graph.pipe(format='svg').decode('utf-8')

class RelatedTables(Graph):

    def __init__(
            self, schema_name: str, table_name: str, depth: int, onlyrefs: bool = False, graph_name: str = None,
            engine: str = 'neato', graph_attr: dict = None, node_attr: dict = None, edge_attr: dict = None) -> None:
        super().__init__(graph_name, engine, graph_attr, node_attr, edge_attr)
        self.tables, self.unvisited_tables = self.__get_related_tables({(schema_name, table_name)}, depth)
        self.onlyrefs = onlyrefs
        return None

    def __get_related_tables(self, unvisited: set[tuple[str, str]], depth: int,
                             visited: set[tuple[str, str]] = None) -> tuple[set, set]:
        if visited is None:
            visited = set()

        if depth == 0:
            return visited.union(unvisited), unvisited

        for schema_name, table_name in unvisited.copy():
            visited.add((schema_name, table_name))
            unvisited.remove((schema_name, table_name))
            for column in self.get_columns(schema_name, table_name):
                for fk_ref in column.fk_references:
                    if (fk_ref.schema, fk_ref.table) not in visited:
                        unvisited.add((fk_ref.schema, fk_ref.table))
                for pk_ref in column.pk_references:
                    if (pk_ref.schema, pk_ref.table) not in visited:
                        unvisited.add((pk_ref.schema, pk_ref.table))
        return self.__get_related_tables(unvisited, depth-1, visited)

    def get_graph(self) -> str:
        digraph = self.build_digraph(self.tables, self.onlyrefs, self.unvisited_tables)
        return self.render_digraph(digraph)