from graphviz import Digraph
import json
import os
from Parser.parser_1 import parse_file
from Parser.struct_dump import _pprint
# from parser_1 import parse_file
# from struct_dump import _pprint
os.environ["PATH"] += os.pathsep + 'C:\\Users\\khaak\\Anaconda3\\Library\\bin\\graphviz'

class Node:
    def __init__(self,node_id,name,pre):
        self.is_event = False
        self.serial_id = node_id ### primary key
        self.pre_1=pre
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
        return ("%s%d" % (self.pre_1,self.serial_id))

class Edge:
    def __init__(self, edge_type, src_node, dst_node, name,id,pre):
        self.edge_type = edge_type ### primary key
        self.src_node = src_node
        self.edge_id=id
        self.dst_node = dst_node
        self.name = name
        self.att=""
        self.colour=""
        self.pre_2=pre
        if self.edge_type=="D":
            self.att="solid"
        elif self.edge_type=="I":
            self.att="dashed"
            self.colour="black"
        elif self.edge_type=="C":
            self.att="dotted"
            self.colour="black"
    def display_id(self,node):
        if node!=None and node>=0:
            return "%s%d" % (self.pre_2,node)
        else :
            # nod=str(node)
            return "%s%d" % (self.pre_2,node)
class Graph:
    def __init__(self, tx_ct,tx1_ct,pre,o_taints,link_taints):
        # self.tx_hash = tx.tx_hash
        # self.event_nodes_map = {} # event_id: int -> node: EventNode
        self.nodes_map = {} # node_id: int -> node: NormalNode
        self.edges_map = {} # edge_id: int -> edge: Edge
        self.pre_f=pre
        self.org=o_taints
        self.link=link_taints
        self.build(tx_ct,tx1_ct)

    def build(self, tx_ct,tx1_ct):
        # register nodes (yet-to-connect):
        for ct in tx_ct:
            for taint in ct.taints:
                print("serial_id",taint.serial_id)
                node = Node(taint.serial_id,taint.name,self.pre_f)
                self.nodes_map[node.display_id()] = node
                # register edges (connect nodes):
                for dep in taint.dependencies:
                    id=len(self.edges_map)
                    edge = Edge(dep.type,dep.source_id,taint.serial_id, dep.name,id,self.pre_f)
                    self.edges_map[edge.edge_id] = edge

        for ct in tx1_ct:
            for taint in ct.taints:
                node = Node(taint.serial_id,taint.name,"b")
                self.nodes_map[node.display_id()] = node
                # register edges (connect nodes):
                for dep in taint.dependencies:
                    id=len(self.edges_map)
                    edge = Edge(dep.type,dep.source_id,taint.serial_id, dep.name,id,"b")
                    self.edges_map[edge.edge_id] = edge
        return

    def render(self, output_filename,val):
        dot = Digraph(comment="TEST")
        # dot.attr("node", fontname="monospace")
        # dot.attr("edge", fontname="monospace")
        # dot.graph_attr["rankdir"] = "BT"
        for node_id in self.nodes_map:
            node = self.nodes_map[node_id]
            # print(node.name,node.serial_id)
            print("node",node.name," ",node.pre_1)
            node_color="orange"
            if node.pre_1==val:
                node_color="blue"
            dot.node(node.display_id(), node.name, shape="oval",color=node_color)
        for edge_id in self.edges_map:
            edge = self.edges_map[edge_id]
            if edge.name=="data" and edge.dst_node in self.org and edge.display_id(edge.dst_node)[0]==val:
                print("Data edge ommited ",edge.src_node,edge.display_id(edge.src_node),edge.display_id(edge.dst_node)," ",edge.dst_node)
            else:
                dot.edge(edge.display_id(edge.src_node), edge.display_id(edge.dst_node), label=edge.name,style=edge.att, color=edge.colour)
            if edge.name=="data" and edge.dst_node in self.link and edge.display_id(edge.dst_node)[0]!=val:
                print("Data Link edge",edge.display_id(edge.src_node),edge.display_id(edge.dst_node)," ",edge.dst_node)
                for t in self.org:
                    temp=val+str(t)
                    dot.edge(edge.display_id(edge.src_node), temp, label=edge.name,
                             style=edge.att, color="green")

                # for t in self.org:

            # print(edge.sr=]
            # ?_node,edge.dst_node)

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

def test(file_name, ind,res):

    assert file_name[-5:] == ".json"
    o_taints=[]
    link_taints=[]
    ind1=0
    for i in res:
        o_taints.append(i)
        val=res[i]
        if val[2]  not in link_taints:
            link_taints.append(val[2])
        file_name1=val[0]
        ind1=val[1]

    l=len(file_name)
    l=l-13
    strt=file_name[0:l]
    file_name1=strt+str(file_name1)+".json"
    print("fil_check",file_name1)


    assert file_name1[-5:] == ".json"
    trace = parse_file(file_name)
    trace_1=parse_file(file_name1)
    print(trace)
    graphs = []
    tx = trace[ind]
    tx1=trace_1[ind1]
    # print("length test",len(trace))
    graph = Graph(tx.call_level_traces,tx1.call_level_traces,"a",o_taints,link_taints)
    # graph1=Graph(tx1.call_level_traces,"b")
    # dot = Digraph(comment=tx.tx_hash)
    # dot.node("A","test")
    # dot.node("B", "test1")
    # dot.node("C","test3")
    # dot.edge("A","B","edge")
    # dot.edge("A","C","test22",style="dotted",color="red")
    # dot.render("test.gv")
    # graph = Graph(tx)
    val="a"
    graph.render("%s.gv" % ("crosslinker_fresh"),val)
    # graph1.render("%s.gv" % ("crosslinker"))
    # graph.render("test.gv")
    graphs.append(graph)
# graphs.append(graph1)
#     print(graphs)
#     _pprint(graphs)

# if __name__ == "__main__":
#     test("./12345678.json",0,"../ContractDB/traces/12345k/12345698.json",0)