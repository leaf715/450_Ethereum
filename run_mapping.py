import json
import difflib
import math
import numpy as np
from dfg_builder import Graph, EventNode, NormalNode
from mapping_sim import map_score
from struct_dump import _pprint
from subgraphs import *

def run_map(file1, file2):
    dfg_test(file1)
    dfg_test(file2)
    map_score(file1, file2)

def dfg_test(file_name):
    from trace_parser import parse_file
    from struct_dump import _pprint
    assert file_name[-5:] == ".json"
    trace = parse_file(file_name)
    graphs = []
    # for i in range(len(trace)):
    # only first transaction in each file for now
    tx = trace[0]
    graph = Graph(tx)
    graph.render("%s_%d.gv" % (file_name[:-5], 0))
    graphs.append(graph)

if __name__ == "__main__":
    run_map("./00048615.json", "./00048643.json")