from typing import Dict, List

from graphviz import Digraph

from .Drawer import Drawer
from ..db import *


class SchemaDrawer(Drawer):
    def __init__(self, tables: List[Table]):
        self.tables: List[Table] = tables

    def to_graph(self) -> Digraph:
        # create graph
        ps = Digraph('Schema',
                     graph_attr={},
                     node_attr={
                         'shape': 'plaintext'
                     })

        # add nodes
        fk_counter: Dict[str, int] = {}

        for table in self.tables:
            columns = "\n".join(self.__column_to_html(table, column, fk_counter) for column in table.columns)

            ps.node(
                table.id,
                f'''<
                    <table border="0" cellborder="1" cellspacing="0" cellpadding="5">
                        <tr>
                            <td><b>{table.name}</b></td>
                        </tr>
                        <tr>
                            <td>
                                <table border="0" cellborder="0" cellspacing="0">
                                    {columns}
                                </table>
                            </td>
                        </tr>
                    </table>
                >'''
            )

        # add edges
        for source_table in self.tables:
            for key in source_table.foreign_keys:
                target_table = key.constraint.table
                fk_counter_key = f'{source_table.name}_{key.constraint.index}'

                ps.edge(source_table.id, target_table.id, label=f'FK{fk_counter[fk_counter_key]}', arrowhead='vee')

        # return graph
        return ps

    @staticmethod
    def __column_to_html(table: Table, column: Column, fk_counter: Dict[str, int]):
        name = column.name

        data_type = column.data_type
        if column.null:
            data_type += ' (NULL)'

        # extract and style column name
        if table.primary_key is not None and column in table.primary_key.columns:
            name = f'<b>{name}</b>'
        for key in table.unique_keys:
            if column in key.columns:
                name = f'<u>{name}</u>'
                break

        # extract foreign keys
        fk = []
        for key in table.foreign_keys:
            if column in key.columns:
                fk_counter_key = f'{table.name}_{key.constraint.index}'
                if fk_counter_key not in fk_counter:
                    fk_counter[fk_counter_key] = max(*fk_counter.values(), 0, 0) + 1

                fk.append(fk_counter[fk_counter_key])

        if len(fk) > 0:
            fk = map(lambda x: f'(FK{x})', sorted(fk))
            fk = f'<i>{" ".join(fk)}</i>'
        else:
            fk = ''

        # convert to html
        return f'''
            <tr port="{column.id}">
                <td align="left">{name}</td>
                <td align="left">: {data_type}</td>
                <td align="left">{fk}</td>
            </tr>
        '''
