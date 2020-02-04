import json
import difflib
import numpy as np
from dfg_builder import Graph, EventNode, NormalNode
from struct_dump import _pprint
from subgraphs import *

def sub_sim(subg1, subg2):
    dlibevent = difflib.SequenceMatcher(None, [node.name for node in subg1.event_nodes_map.values()], [node.name for node in subg2.event_nodes_map.values()])
    dlibnormal = difflib.SequenceMatcher(None, [node.name for node in subg1.normal_nodes_map.values()], [node.name for node in subg2.normal_nodes_map.values()])
    return (dlibevent.ratio()+dlibnormal.ratio())/2

def test(file1, file2):
    subgraphs = load_subgraphs(file1, file2)
    print(file1)
    for subgraph in subgraphs[0]:
            print(str(len(subgraph.event_nodes_map)) + " " + str(len(subgraph.normal_nodes_map)))
    print(file2)
    for subgraph in subgraphs[1]:
            print(str(subgraph.event_count) + " " + str(subgraph.normal_count))
    sgmatrix = []
    if len(subgraphs[0]) > len(subgraphs[1]):
        r = 1
        c = 0
    else:
        r = 0
        c = 1
    for sub1 in subgraphs[r]:
        v = []
        for sub2 in subgraphs[c]:
            v.append(str(round(sub_sim(sub1, sub2), 2)))
        sgmatrix.append(v)
    npmat = np.array(sgmatrix)
    mappedsgs = []
    print(npmat)
    for i in range(len(subgraphs[r])):
        (x, y) = np.unravel_index(np.argmax(npmat, axis=None), npmat.shape)
        mappedsgs.append((subgraphs[r][x], subgraphs[c][y], npmat[x][y]))
        npmat[x] = 0
        npmat[:,y] = 0
        print(npmat)
    for a, b, c in mappedsgs:
        print(a.key_node + " -> "+b.key_node+": "+c)
        print(str(a.event_count) + " " + str(a.normal_count)+" -> "+str(b.event_count) + " " + str(b.normal_count))

if __name__ == "__main__":
    test("./04501736.json", "./04501969.json")
