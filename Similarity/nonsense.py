import json
import difflib
import numpy as np
import sys
from dfg_builder import Graph, EventNode, NormalNode
from struct_dump import _pprint
from subgraphs import *
from run_mapping import *

dfg_test("./00469642.json", 0)
