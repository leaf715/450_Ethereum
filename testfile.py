import json
import difflib
import numpy as np
from dfg_builder import Graph, EventNode, NormalNode
from struct_dump import _pprint
from subgraphs import *

print(difflib.SequenceMatcher(None, [1,1,1,1], [1,1,1,1,1]).ratio())
print(difflib.SequenceMatcher(None, [1,1,1,1,2], [1,1,1,1,1]).ratio())
