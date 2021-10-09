import json
import gzip

from graphviz import Digraph

from erd_viewer.database import Column, SchemaTableColumn, SchemaTable
from erd_viewer.loader.redis import RedisClient
from erd_viewer.loader.loader import DBJSONDecoder

class Graph:

    _HTML_TABLE_TEMPLATE = '<<table>{thead}{tbody}</table>>'
    _HTML_TABLE_HEAD_TEMPLATE = '<tr><td colspan="2">{thead}</td></tr>'
    _HTML_TABLE_BODY_TEMPLATE = '{tbody}'
    _HTML_TABLE_ROW_TEMPLATE = '<tr><td port="{port}">{name}</td><td>{datatype}</td></tr>'

    _graph_attr = {'overlap': 'prism', 'splines': 'spline'}
    _node_attr = {'shape': 'plaintext'}

    def __init__(self, graph_name: str = None, engine: str = 'neato',
                 graph_attr: dict = None, node_attr: dict = None, edge_attr: dict = None) -> None:
        self.graph_name = graph_name
        self.engine = engine

        self.graph_attr = graph_attr if graph_attr else self._graph_attr
        self.node_attr = node_attr if node_attr else self._node_attr
        self.edge_attr = edge_attr

        self.redis = RedisClient().get_client()
        return None

    def get_columns(self, schema_table: SchemaTable) -> list:
        json_columns = self.redis.hget(schema_table.schema, schema_table.table)
        if isinstance(json_columns, bytes):
            return json.loads(json_columns.decode('utf-8'), cls=DBJSONDecoder)
        return []

    def _get_html_table(self, schema: str, table: str, columns: list[Column]) -> str:
        thead = self._HTML_TABLE_HEAD_TEMPLATE.format(thead='.'.join([schema, table]))
        tbody = ''
        for column in columns:
            tbody += self._HTML_TABLE_ROW_TEMPLATE.format(
                port=column.name,
                name=column.name,
                datatype=column.type
            )

        tbody = self._HTML_TABLE_BODY_TEMPLATE.format(tbody=tbody)
        return self._HTML_TABLE_TEMPLATE.format(thead=thead, tbody=tbody)

    def _generate_refs(
        self,
        tables_with_columns: dict[SchemaTable, list[Column]],
        unvisited_tables: set[SchemaTable] = None
        ) -> list[tuple[SchemaTableColumn, SchemaTableColumn]]:

        if unvisited_tables is None:
            unvisited_tables = set()

        refs = []

        for schema_table, columns in tables_with_columns.items():
            for column in columns:
                if schema_table not in unvisited_tables:
                    for fk_ref in column.fk_references:
                        if SchemaTable(fk_ref.schema, fk_ref.table) in tables_with_columns:
                            refs.append(
                                (SchemaTableColumn(schema_table.schema, schema_table.table, column.name),
                                fk_ref)
                            )
                else:
                    for fk_ref in column.fk_references:
                        if SchemaTable(fk_ref.schema, fk_ref.table) in set(tables_with_columns).difference(unvisited_tables):
                            refs.append(
                                (SchemaTableColumn(schema_table.schema, schema_table.table, column.name),
                                fk_ref)
                            )
        return refs

    def _fill_digraph(self, digraph: Digraph, tables_with_columns: dict[SchemaTable, list[Column]],
                     refs: list[tuple[SchemaTableColumn, SchemaTableColumn]]) -> Digraph:

        for schema_table, columns in tables_with_columns.items():
            digraph.node(
                name=f'{schema_table.schema}.{schema_table.table}',
                label=self._get_html_table(schema_table.schema, schema_table.table, columns)
            )

        for stc1, stc2 in refs:
            digraph.edge(
                tail_name=f'{stc1.schema}.{stc1.table}:{stc1.column}',
                head_name=f'{stc2.schema}.{stc2.table}:{stc2.column}'
            )

        return digraph

    def build_digraph(self, tables: set[SchemaTable], onlyrefs: bool = False,
                      unvisited_tables: set[SchemaTable] = None) -> Digraph:
        digraph = Digraph(name=self.graph_name, engine=self.engine, graph_attr=self.graph_attr,
                          node_attr=self.node_attr, edge_attr=self.edge_attr)

        tables_with_columns = {schema_table: self.get_columns(schema_table) for schema_table in tables}

        refs = self._generate_refs(tables_with_columns, unvisited_tables)

        if onlyrefs:
            unique_columns = {stc for t in refs for stc in t}

            for schema_table, columns in tables_with_columns.items():
                filtered_columns = []
                for column in columns:
                    if SchemaTableColumn(schema_table.schema, schema_table.table, column.name) in unique_columns:
                        filtered_columns.append(column)
                tables_with_columns[schema_table] = filtered_columns

        return self._fill_digraph(digraph, tables_with_columns, refs)

    def render_digraph(self, graph: Digraph) -> bytes:
        return gzip.compress(graph.pipe(format='svg'), compresslevel=9)

class RelatedTables(Graph):

    def __init__(
            self, schema_table: SchemaTable, depth: int, tables_to_exclude: list[SchemaTable], onlyrefs: bool = False,
            graph_name: str = None, engine: str = 'neato', graph_attr: dict = None, node_attr: dict = None, edge_attr: dict = None) -> None:
        super().__init__(graph_name, engine, graph_attr, node_attr, edge_attr)
        self.tables, self.unvisited_tables = self._get_related_tables({schema_table}, depth, tables_to_exclude)
        self.onlyrefs = onlyrefs
        return None

    def _get_related_tables(self, unvisited: set[SchemaTable], depth: int, tables_to_exclude: list[SchemaTable],
                             visited: set[SchemaTable] = None) -> tuple[set, set]:
        if visited is None:
            visited = set()

        if depth == 0:
            return visited.union(unvisited), unvisited

        for schema_table in unvisited.copy():
            visited.add(schema_table)
            unvisited.remove(schema_table)
            for column in self.get_columns(schema_table):
                for ref in column.fk_references + column.pk_references:
                    ref_schema_table = SchemaTable(ref.schema, ref.table)
                    if ref_schema_table not in visited and ref_schema_table not in tables_to_exclude:
                        unvisited.add(ref_schema_table)

        return self._get_related_tables(unvisited, depth-1, tables_to_exclude, visited)

    def get_graph(self) -> bytes:
        digraph = self.build_digraph(self.tables, self.onlyrefs, self.unvisited_tables)
        return self.render_digraph(digraph)
