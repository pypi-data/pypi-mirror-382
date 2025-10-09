from graphviz import Digraph


class Drawer:
    def to_graph(self) -> Digraph:
        raise NotImplementedError

    def to_svg(self, lr: bool) -> str:
        ps = self.to_graph()
        if lr:
            ps.graph_attr['rankdir'] = 'LR'

        return ps.pipe(format='svg').decode('utf-8')
