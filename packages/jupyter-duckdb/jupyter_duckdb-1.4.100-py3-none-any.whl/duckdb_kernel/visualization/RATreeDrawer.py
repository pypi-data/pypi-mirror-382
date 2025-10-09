from typing import Dict, Optional

from graphviz import Digraph
from uuid import uuid4

from duckdb_kernel.db import Table
from duckdb_kernel.parser.elements import RAElement
from duckdb_kernel.util.formatting import row_count
from .Drawer import Drawer
from ..db import Connection
from .lib import *


class RATreeDrawer(Drawer):
    def __init__(self, db: Connection, root_node: RAElement, tables: Dict[str, Table]):
        self.db: Connection = db
        self.root_node: RAElement = root_node
        self.tables: Dict[str, Table] = tables

        self.nodes: Dict[str, RAElement] = {}
        self.root_node_id: Optional[str] = None

    def to_graph(self) -> Digraph:
        # create graph
        ps = Digraph('Schema',
                     graph_attr={},
                     node_attr={
                         'shape': 'plaintext'
                     })

        # add nodes
        self.__add_node(ps, self.root_node)

        # return graph
        return ps

    def __add_node(self, ps: Digraph, node: RAElement) -> str:
        # use id of node object as identifier
        node_id = f'node_{str(uuid4()).replace("-", "_")}'

        self.nodes[node_id] = node
        if node == self.root_node:
            self.root_node_id = node_id

        # generate child nodes
        child_ids = [self.__add_node(ps, child) for child in node.children]

        # create node
        count_query = node.to_sql_with_count(self.tables)
        _, ((count,),) = self.db.execute(count_query)

        if node.conditions is None:
            conditions = ''
        else:
            condition_str = node.conditions.replace('<', '&lt;').replace('>', '&gt;')
            conditions = f'<tr><td>{condition_str}</td></tr>'

        ps.node(
            node_id,
            f'''<
                <table border="0" cellborder="1" cellspacing="0" cellpadding="5">
                    <tr>
                        <td><b>{node.name}</b></td>
                    </tr>
                    
                    {conditions}
                    
                    <tr>
                        <td>{row_count(count)}</td>
                    </tr>
                </table>
            >'''
        )

        # add edges from node to children
        for child_id in child_ids:
            ps.edge(node_id, child_id, arrowhead='none')

        # return node identifier to generate edges
        return node_id

    def to_interactive_svg(self) -> str:
        div_id = f'div-{str(uuid4())}'

        css = init_css()
        ra = init_ra()
        svg = self.to_svg(True)

        return f'''
            <style type="text/css">
                {css}
            </style>
            
            <div id="{div_id}">
                {svg}
            </div>
            
            <script type="text/javascript">
                {ra}
                
                animate_ra('{div_id}', '{self.root_node_id}')
            </script>
        '''
