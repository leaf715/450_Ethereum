import json
import os
import glob
import shutil
from parser_dest import Dependency, Taint, Output, CallLevelTrace, TransactionLevelTrace, parse_file
from struct_dump import _pprint

class Transformer:
    def get_trace(self, dir, i):
        return dir+self.num_str8(i)[:5]+"k/"+i+".json"

    def num_str8(self, i):
        num_str = str(i)
        return "0"*(8-len(num_str))+num_str

    def __init__(self, trace_dir, trace):
        self.DFG = parse_file(self.get_trace(trace_dir, self.num_str8(trace)))
        # _pprint(self.DFG)

    def graybox_call(self):
        pass

    def graybox_trxn(self):
        pass

if __name__ == "__main__":
    trs = Transformer("traces/", 12345678)
