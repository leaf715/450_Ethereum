from graphviz import Digraph

class Node:
    def __init__(self,node_id,name):
        self.is_event = False
        self.serial_id = node_id ### primary key
        self.name = name

    def display_id(self):
        return "n%d" % self.serial_id

class Edge:
    def __init__(self, edge_type, src_node, dst_node, name,id):
        self.edge_type = edge_type ### primary key
        self.src_node = src_node
        self.edge_id=id
        self.dst_node = dst_node
        self.name = name
        self.att=""
        self.colour=""
        if self.edge_type=="D":
            self.att="solid"
        elif self.edge_type=="I":
            self.att="dashed"
            self.colour="red"
        elif self.edge_type=="C":
            self.att="dotted"
            self.colour="blue"
    def display_id(self,node):
        if node!=None and node>=0:
            return "n%d" % node
        else :
            nod=str(node)
            return nod
class Graph:
    def __init__(self, tx_ct):
        self.nodes_map = {} # node_id: int -> node: Node
        self.edges_map = {} # edge_id: int -> edge: Edge
        self.build(tx_ct)

    def build(self, tx_ct):
        # register nodes (yet-to-connect):
        for ct in tx_ct:
            for taint in ct.taints:
                node = Node(taint.serial_id,taint.name)
                self.nodes_map[node.serial_id] = node
                # register edges (connect nodes):
                for dep in taint.dependencies:
                    id=len(self.edges_map)
                    edge = Edge(dep.type,dep.source_id,taint.serial_id, dep.name,id)
                    self.edges_map[edge.edge_id] = edge
        return

    def render(self, output_filename):
        dot = Digraph(comment="TEST")
        # dot.attr("node", fontname="monospace")
        # dot.attr("edge", fontname="monospace")
        # dot.graph_attr["rankdir"] = "BT"
        for node_id in self.nodes_map:
            node = self.nodes_map[node_id]
            dot.node(node.display_id(), node.name, shape="oval")
        for edge_id in self.edges_map:
            edge = self.edges_map[edge_id]
            dot.edge(edge.display_id(edge.src_node), edge.display_id(edge.dst_node), label=edge.name,style=edge.att,color=edge.colour)
        dot.render(output_filename, view=False)


def test(file_name, ind):
    from parser_1 import parse_file
    from struct_dump import _pprint
    assert file_name[-5:] == ".json"
    trace = parse_file(file_name)
    print(trace)
    graphs = []
    tx = trace[ind]
    graph = Graph(tx.call_level_traces)
    graph.render("%s_%d.gv" % (file_name[:-5], ind))
    graphs.append(graph)
    _pprint(graphs)

if __name__ == "__main__":
    test("./12345678.json",0)