import json
import difflib
import math
import time
import numpy as np
from dfg_builder import Graph, EventNode, NormalNode
from mapping_sim import map_score
from struct_dump import _pprint
from subgraphs import *

def run_map(file1, ind1, file2, ind2, draw):
    if draw:
        dfg_test(file1, ind1)
        dfg_test(file2, ind2)
    map_score(file1, ind1, file2, ind2)

def dfg_test(file_name, ind):
    from trace_parser import parse_file
    from struct_dump import _pprint
    assert file_name[-5:] == ".json"
    trace = parse_file(file_name)
    graphs = []
    # for i in range(len(trace)):
    # only first transaction in each file for now
    tx = trace[ind]
    graph = Graph(tx)
    graph.render("%s_%d.gv" % (file_name[:-5], ind))
    graphs.append(graph)

if __name__ == "__main__":
    start_time = time.time()
    run_map("./00469642.json", 1, "./00469649.json", 0, False)
    print("Runtime: "+str(time.time()-start_time))
