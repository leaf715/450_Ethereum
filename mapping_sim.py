import json
import difflib
import math
import numpy as np
from dfg_builder import Graph, EventNode, NormalNode
from struct_dump import _pprint
from subgraphs import *

def degree_hist(nodes1, nodes2):
    hscore = 0
    his1 = {}
    his2 = {}
    for node in nodes1:
        degree = len(node.src_edge_ids) + len(node.dst_edge_ids)
        if degree in his1:
            his1[degree] += 1
        else:
            his1[degree] = 1
    for node in nodes2:
        degree = len(node.src_edge_ids) + len(node.dst_edge_ids)
        if degree in his2:
            his2[degree] += 1
        else:
            his2[degree] = 1
    maxdegree = max(max(his1.keys()), max(his2.keys()))
    diff = []
    for i in range(maxdegree+1):
        if i in his1:
            x = his1[i]
        else:
            x = 0
        if i in his2:
            y = his2[i]
        else:
            y = 0
        if (x+y) > 0:
            diff.append((abs(x-y), (x+y)))
        else:
            diff.append((0, -1))
    hscores = [(j-i)/j for i, j in diff[1:]]
    denom = 0
    for i, j in enumerate(hscores):
        if j > 0:
            hscore+=j*(i+1)
            denom+=i+1
    hscore/=denom
    # print(diff)
    # print(his1)
    # print(his2)
    # print(hscores)
    # print(hscore)
    return hscore

def sub_sim(subg1, subg2):
    dlibevent = difflib.SequenceMatcher(None, [node.name for node in subg1.event_nodes_map.values()], [node.name for node in subg2.event_nodes_map.values()])
    dlibnormal = difflib.SequenceMatcher(None, [node.name for node in subg1.normal_nodes_map.values()], [node.name for node in subg2.normal_nodes_map.values()])
# changing ratio() to quick_ratio() reduces runtime ~ 50% but increases score ~ 20
    eventscore = dlibevent.ratio()
    normalscore = dlibnormal.ratio()
    dlibedges = difflib.SequenceMatcher(None, [(edge.dst_node.name, edge.src_node.name) for edge in subg1.edges_map.values()], [(edge.dst_node.name, edge.src_node.name) for edge in subg2.edges_map.values()])
    edgescore = dlibedges.ratio()
    # https://s3.amazonaws.com/academia.edu.documents/30842376/structure_based_similarity_search_with_graph_histograms.pdf?response-content-disposition=inline%3B%20filename%3DStructure-based_similarity_search_with_g.pdf&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWOWYYGZ2Y53UL3A%2F20200205%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20200205T210625Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=fc6ab5ccee4444e145d0b50d48cdf2500d8d662044f4fcde7b523684cb3f463c
    hscore = degree_hist(subg1.normal_nodes_map.values(), subg2.normal_nodes_map.values())
    return (2*eventscore + 1.5*normalscore + 1.5*edgescore + hscore)/6

def map_score(file1, ind1, file2, ind2):
    subgraphs = load_subgraphs(file1, ind1, file2, ind2)
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
            v.append(sub_sim(sub1, sub2))
        sgmatrix.append(v)
    npmat = np.array(sgmatrix)
    mappedsgs = []
    matched = []
    for i in range(len(subgraphs[r])):
        (x, y) = np.unravel_index(np.argmax(npmat, axis=None), npmat.shape)
        mappedsgs.append((subgraphs[r][x], subgraphs[c][y], npmat[x][y]))
        matched.append(int(y))
        npmat[x] = 0
        npmat[:,y] = 0
    for a, b, score in mappedsgs:
        print(a.key_node + " -> "+b.key_node+": "+str(round(score,2)))
        print(str(a.event_count) + " " + str(a.normal_count)+" -> "+str(b.event_count) + " " + str(b.normal_count))
    unmatched = [j for i, j in enumerate(subgraphs[c]) if i not in matched]
    for subg in unmatched:
        print(subg.key_node)
    tscore = 0
    factor = 0
    for a, b, score in mappedsgs:
        f = math.sqrt((a.event_count + a.normal_count + b.event_count + b.normal_count)/2)
        tscore+=f*score
        factor+=f
    for subg in unmatched:
        factor+=math.sqrt((subg.event_count + subg.normal_count)/2)
    simscore = tscore/factor
    print(simscore)
    return simscore


if __name__ == "__main__":
    map_score("./04501736.json", "./04501969.json")
