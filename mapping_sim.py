import json
from dfg_builder import Graph, EventNode, NormalNode
from struct_dump import _pprint
from subgraphs import *

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
