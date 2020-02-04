from graphviz import Digraph
import json

class EventNode:
    def __init__(self, event_id, call_nonce, name):
        self.is_event = True
        self.node_id = None
        self.event_id = event_id ### primary key
        self.call_nonce = call_nonce
        self.name = name
        self.extra_info = None # An event_node has no extra_info.
        self.src_edge_ids = [] # (Maintain after initialization)
        self.dst_edge_ids = None # An event_node has no dst_edges.
    def _display_id(self):
        return "e%d" % self.event_id

class NormalNode:
    def __init__(self, node_id, call_nonce, extra_info, name):
        self.is_event = False
        self.node_id = node_id ### primary key
        self.event_id = None
        self.call_nonce = call_nonce
        self.name = name
        self.extra_info = extra_info
        self.src_edge_ids = [] # (Maintain after initialization)
        self.dst_edge_ids = [] # (Maintain after initialization)
    def _display_name(self):
        shortened_info = [s if len(s) <= 12 else "0x%s..%s" % (s[2:6], s[-4:]) for s in self.extra_info]
        return "_".join([self.name] + shortened_info)
    def _display_id(self):
        return "n%d" % self.node_id

class Edge:
    def __init__(self, edge_id, src_node, dst_node, name):
        self.edge_id = edge_id ### primary key
        self.src_node = src_node
        self.dst_node = dst_node
        self.name = name

class Graph:
    def __init__(self, tx):
        self.tx_hash = tx.tx_hash
        self.event_nodes_map = {} # event_id: int -> node: EventNode
        self.normal_nodes_map = {} # node_id: int -> node: NormalNode
        self.edges_map = {} # edge_id: int -> edge: Edge
        self.build(tx)

    def build(self, tx):
        # register normal nodes (yet-to-connect):
        for node in tx.plain_nodes:
            normal_node = NormalNode(
                node.node_id, node.call_nonce, node.extra_info, node.name
            )
            self.normal_nodes_map[node.node_id] = normal_node
        # register event nodes (connected) (and a part of edges):
        for call_trace in tx.call_traces:
            for event in call_trace.events:
                event_node = EventNode(
                    event.event_id, call_trace.call_nonce, event.name
                )
                for argument in event.arguments:
                    edge_name = argument.name
                    for segment in argument.segments:
                        if segment.dfg_node_id is None:
                            continue
                        source_node = self.normal_nodes_map[segment.dfg_node_id]
                        if segment.offset is not None:
                            edge_name += "[%s]" % segment.offset
                        edge_id = len(self.edges_map)
                        edge = Edge(
                            edge_id, source_node, event_node, edge_name
                        )
                        event_node.src_edge_ids.append(edge_id)
                        source_node.dst_edge_ids.append(edge_id)
                        self.edges_map[edge_id] = edge
                self.event_nodes_map[event.event_id] = event_node
        # connect normal nodes:
        for node in tx.plain_nodes:
            for i in range(len(node.source_node_ids)):
                source_node_id = node.source_node_ids[i]
                source_node = self.normal_nodes_map[source_node_id]
                destination_node = self.normal_nodes_map[node.node_id]
                edge_name = "arg%d" % i
                edge_id = len(self.edges_map)
                edge = Edge(
                    edge_id, source_node, destination_node, edge_name
                )
                source_node.dst_edge_ids.append(edge_id)
                destination_node.src_edge_ids.append(edge_id)
                self.edges_map[edge_id] = edge
        return

    def render(self, output_filename):
        dot = Digraph(comment=self.tx_hash)
        dot.attr("node", fontname="monospace")
        dot.attr("edge", fontname="monospace")
        dot.graph_attr["rankdir"] = "BT"
        for event_node_id in self.event_nodes_map:
            node = self.event_nodes_map[event_node_id]
            name = "%d %d %s" % (node.call_nonce, node.event_id, node.name)
            dot.node(node._display_id(), name, shape="box")
        for normal_node_id in self.normal_nodes_map:
            node = self.normal_nodes_map[normal_node_id]
            name = "%d %d %s" % (node.call_nonce, node.node_id, node._display_name())
            dot.node(node._display_id(), name, shape="oval")
        for edge_id in self.edges_map:
            edge = self.edges_map[edge_id]
            dot.edge(edge.src_node._display_id(), edge.dst_node._display_id(), label=edge.name)
        dot.render(output_filename, view=False)

    def successors_of(self, node):
        if node.is_event:
            return [], []
        edges = [self.edges_map[edge_id] for edge_id in node.dst_edge_ids]
        nodes = [edge.dst_node for edge in edges]
        edge_labels = [edge.name for edge in edges]
        return nodes, edge_labels

    def predecessors_of(self, node):
        edges = [self.edges_map[edge_id] for edge_id in node.src_edge_ids]
        nodes = [edge.src_node for edge in edges]
        edge_labels = [edge.name for edge in edges]
        return nodes, edge_labels


def test(file_name):
    from trace_parser import parse_file
    from struct_dump import _pprint
    assert file_name[-5:] == ".json"
    trace = parse_file(file_name)
    graphs = []
    for i in range(len(trace)):
        tx = trace[i]
        graph = Graph(tx)
        graph.render("%s_%d.gv" % (file_name[:-5], i))
        graphs.append(graph)
    _pprint(graphs)

if __name__ == "__main__":
    test("./04501969.json")

# $ python3 dfg_builder.py > test_builder_04501969.json
