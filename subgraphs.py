import json
from dfg_builder import Graph, EventNode, NormalNode
from struct_dump import _pprint

class SubGraph:
    def __init__(self):
        self.event_nodes_map = {} # event_id: int -> node: EventNode
        self.normal_nodes_map = {} # node_id: int -> node: NormalNode
        self.edges_map = {} # edge_id: int -> edge: Edge
        self.event_count = 0
        self.normal_count = 0
        self.key_node = None

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

def load_subgraphs(file1, file2):
    from trace_parser import parse_file
    from struct_dump import _pprint
    assert file1[-5:] == ".json"
    assert file2[-5:] == ".json"
    trace = parse_file(file1)
    graphs = []
    for i in range(len(trace)):
        tx = trace[i]
        graph = Graph(tx)
        graphs.append(graph)
    trace = parse_file(file2)
    for i in range(len(trace)):
        tx = trace[i]
        graph = Graph(tx)
        graphs.append(graph)
    subgraphs = []
    for i in graphs:
        subgraphs.append(get_subgraphs(i))
    return subgraphs

def get_subgraphs(graph):
    visited = set()
    subgraphs = []
    for event_node in graph.event_nodes_map.values():
        if (event_node.event_id, True) not in visited:
            subgraph = SubGraph()
            subgraph.event_nodes_map[event_node.event_id] = event_node
            enqueue = []
            for i in event_node.src_edge_ids:
                edge = graph.edges_map[i]
                subgraph.edges_map[i] = edge
                enqueue.append((edge.src_node.node_id, edge.src_node.is_event))
            while enqueue:
                (node_id, isevent) = enqueue.pop()
                if (node_id, isevent) not in visited:
                    if isevent:
                        new_node = graph.event_nodes_map[node_id]
                        subgraph.event_nodes_map[node_id] = new_node
                        for i in new_node.src_edge_ids:
                            edge = graph.edges_map[i]
                            subgraph.edges_map[i] = edge
                            enqueue.append((edge.src_node.node_id, edge.src_node.is_event))
                    else:
                        new_node = graph.normal_nodes_map[node_id]
                        subgraph.normal_nodes_map[node_id] = new_node
                        for i in new_node.src_edge_ids:
                            edge = graph.edges_map[i]
                            subgraph.edges_map[i] = edge
                            enqueue.append((edge.src_node.node_id, edge.src_node.is_event))
                        for i in new_node.dst_edge_ids:
                            edge = graph.edges_map[i]
                            subgraph.edges_map[i] = edge
                            if isinstance(edge.dst_node, NormalNode):
                                enqueue.append((edge.dst_node.node_id, edge.dst_node.is_event))
                            elif isinstance(edge.dst_node, EventNode):
                                enqueue.append((edge.dst_node.event_id, edge.dst_node.is_event))
                            else:
                                print("error: node is not event or normal")
                visited.add((node_id, isevent))

            visited.add((event_node.event_id, True))
            subgraph.event_count = len(subgraph.event_nodes_map)
            subgraph.normal_count = len(subgraph.normal_nodes_map)
            subgraph.key_node = str(event_node.call_nonce)+" "+str(event_node.event_id)+" "+event_node.name
            subgraphs.append(subgraph)
            print(str(event_node.call_nonce)+" "+str(event_node.event_id)+" "+event_node.name)
            print(str(len(subgraph.event_nodes_map)) + " " + str(len(subgraph.normal_nodes_map)))
    subgraphs.sort(key=lambda x: x.event_count + x.normal_count, reverse=True)
    return subgraphs


def test(file1, file2):
    subgraphs = load_subgraphs(file1, file2)
    print(file1)
    for subgraph in subgraphs[0]:
            print(str(len(subgraph.event_nodes_map)) + " " + str(len(subgraph.normal_nodes_map)))
    print(file2)
    for subgraph in subgraphs[1]:
            print(str(subgraph.event_count) + " " + str(subgraph.normal_count))
    # _pprint(subgraphs1[0])




if __name__ == "__main__":
    test("./04501736.json", "./04501969.json")
