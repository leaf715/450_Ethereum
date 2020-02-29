from graphviz import Digraph
import json
import os
os.environ["PATH"] += os.pathsep + 'C:\\Users\\khaak\\Anaconda3\\Library\\bin\\graphviz'

class Node:
    def __init__(self,node_id,name):
        self.is_event = False
        self.serial_id = node_id ### primary key
        # self.event_id = None
        # self.call_nonce = call_nonce
        self.name = name
        # self.extra_info = extra_info
        # self.src_edge_ids = [] # (Maintain after initialization)
        # self.dst_edge_ids = [] # (Maintain after initialization)
    # def _display_name(self):
    #     shortened_info = [s if len(s) <= 12 else "0x%s..%s" % (s[2:6], s[-4:]) for s in self.extra_info]
    #     return "_".join([self.name] + shortened_info)
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
        # self.tx_hash = tx.tx_hash
        # self.event_nodes_map = {} # event_id: int -> node: EventNode
        self.nodes_map = {} # node_id: int -> node: NormalNode
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
            # print(node.name,node.serial_id)
            dot.node(node.display_id(), node.name, shape="oval")
        for edge_id in self.edges_map:
            edge = self.edges_map[edge_id]
            # print(edge.sr=]
            # ?_node,edge.dst_node)
            dot.edge(edge.display_id(edge.src_node), edge.display_id(edge.dst_node), label=edge.name,style=edge.att,color=edge.colour)
        dot.render(output_filename, view=False)

    # def successors_of(self, node):
    #     if node.is_event:
    #         return [], []
    #     edges = [self.edges_map[edge_id] for edge_id in node.dst_edge_ids]
    #     nodes = [edge.dst_node for edge in edges]
    #     edge_labels = [edge.name for edge in edges]
    #     return nodes, edge_labels
    #
    # def predecessors_of(self, node):
    #     edges = [self.edges_map[edge_id] for edge_id in node.src_edge_ids]
    #     nodes = [edge.src_node for edge in edges]
    #     edge_labels = [edge.name for edge in edges]
    #     return nodes, edge_labels

def test(file_name, ind):
    from parser_1 import parse_file
    from struct_dump import _pprint
    assert file_name[-5:] == ".json"
    trace = parse_file(file_name)
    print(trace)
    graphs = []
    tx = trace[ind]
    graph = Graph(tx.call_level_traces)
    # dot = Digraph(comment=tx.tx_hash)
    # dot.node("A","test")
    # dot.node("B", "test1")
    # dot.node("C","test3")
    # dot.edge("A","B","edge")
    # dot.edge("A","C","test22",style="dotted",color="red")
    # dot.render("test.gv")
    # graph = Graph(tx)
    graph.render("%s_%d.gv" % (file_name[:-5], ind))
    # graph.render("test.gv")
    graphs.append(graph)
    _pprint(graphs)

if __name__ == "__main__":
    test("./12345678.json",0)