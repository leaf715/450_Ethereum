import json
import os
import glob
import shutil
from parser import Dependency, Taint, Output, CallLevelTrace, TransactionLevelTrace, parse_file
from struct_dump import _pprint
from visualization import Graph

blockinfo = set([-2, -3, -5, -6])

class GreyDependency:
    def __init__(self, type, source, name = None):
        if name == None:
            name = ""
        self.type=type
        self.source_id=source
        self.name=name

class GreyTaint:
    def __init__(self, taint, greydeps):
        self.serial_id=taint.serial_id
        self.pc=taint.pc
        self.name=taint.name
        self.value=taint.value
        self.dependencies=greydeps
        self.Dsource_ids = taint.Dsource_ids
        self.Isource_ids = taint.Isource_ids
        self.Csource_ids = taint.Csource_ids
        self.Ddestination_ids = taint.Ddestination_ids
        self.Idestination_ids = taint.Idestination_ids
        self.Cdestination_ids = taint.Cdestination_ids

class Transformer:
    def get_trace(self, dir, i):
        return dir+self.num_str8(i)[:5]+"k/"+i+".json"

    def num_str8(self, i):
        num_str = str(i)
        return "0"*(8-len(num_str))+num_str

    # parces trace [trace] in directory [trace_dir]
    def __init__(self, trace_dir, trace):
        self.DFG = parse_file(self.get_trace(trace_dir, self.num_str8(trace)))

    # transform call [call_id] in trxn [tx_id] from white box to grey box
    def greybox_call(self, tx_id, call_id):
        call_trace_dict = {}
        taint_dict = {}
        outputset = set()
        tx = self.DFG[tx_id]
        greycalls = []
        for call in tx.call_level_traces:
            for taint in call.taints:
                call_trace_dict[taint.serial_id] = call.call_id
                taint_dict[taint.serial_id] = taint
            for output in call.outputs:
                outputset.add(output.trigger_id)

        call = tx.call_level_traces[call_id]

        lhset = set()
        rhset = set()
        greytaints = set()
        greydependencies = {}
        for taint in call.taints:
            for id in taint.Dsource_ids:
                if id in blockinfo:
                    if id in greydependencies:
                        greydependencies[taint.serial_id].add(GreyDependency("D", id))
                    else:
                        greydependencies[taint.serial_id] = set([GreyDependency("D", id)])
                    lhset.add(taint)
                    greytaints.add(taint)
                if id in call_trace_dict:
                    if call_trace_dict[id] != call.call_id:
                        lhset.add(taint)
                        greytaints.add(taint)
                elif id >= 0:
                    lhset.add(taint)
                    greytaints.add(taint)
            for id in taint.Ddestination_ids:
                if id in call_trace_dict:
                    if call_trace_dict[id] != call.call_id:
                        rhset.add(taint)
                        greytaints.add(taint)
            if taint.serial_id in outputset:
                for id in taint.Dsource_ids.union(taint.Isource_ids):
                    rhset.add(taint_dict[id])
                    greytaints.add(taint_dict[id])
        for ltaint in lhset:
            for source_id in ltaint.Dsource_ids:
                if source_id in call_trace_dict:
                    if call_trace_dict[source_id] == call.call_id and taint_dict[source_id] not in lhset:
                        greytaints.add(taint_dict[source_id])
                        if ltaint.serial_id in greydependencies:
                            greydependencies[ltaint.serial_id].add(GreyDependency("D", source_id))
                        else:
                            greydependencies[ltaint.serial_id] = set([GreyDependency("D", source_id)])
            for source_id in ltaint.Isource_ids:
                if source_id in call_trace_dict:
                    if call_trace_dict[source_id] == call.call_id:
                        greytaints.add(taint_dict[source_id])
                        if ltaint.serial_id in greydependencies:
                            greydependencies[ltaint.serial_id].add(GreyDependency("I", source_id))
                        else:
                            greydependencies[ltaint.serial_id] = set([GreyDependency("I", source_id)])
            for rtaint in rhset:
                if ltaint.serial_id == rtaint.serial_id:
                    if rtaint.serial_id in greydependencies:
                        greydependencies[rtaint.serial_id].add(GreyDependency("Identical", ltaint.serial_id))
                    else:
                        greydependencies[rtaint.serial_id] = set([GreyDependency("Identical", ltaint.serial_id)])
                elif ltaint.serial_id in rtaint.Dsource_ids and ltaint.serial_id not in rtaint.Isource_ids.union(rtaint.Csource_ids):
                    if rtaint.serial_id in greydependencies:
                        greydependencies[rtaint.serial_id].add(GreyDependency("D", ltaint.serial_id))
                    else:
                        greydependencies[rtaint.serial_id] = set([GreyDependency("D", ltaint.serial_id)])
                elif ltaint.serial_id in rtaint.Dsource_ids.union(rtaint.Isource_ids) and ltaint.serial_id not in rtaint.Csource_ids:
                    if rtaint.serial_id in greydependencies:
                        greydependencies[rtaint.serial_id].add(GreyDependency("I", ltaint.serial_id))
                    else:
                        greydependencies[rtaint.serial_id] = set([GreyDependency("I", ltaint.serial_id)])
                elif ltaint.serial_id in rtaint.Dsource_ids.union(rtaint.Isource_ids, rtaint.Csource_ids):
                    if rtaint.serial_id in greydependencies:
                        greydependencies[rtaint.serial_id].add(GreyDependency("C", ltaint.serial_id))
                    else:
                        greydependencies[rtaint.serial_id] = set([GreyDependency("C", ltaint.serial_id)])
        for rtaint in rhset:
            for id in rtaint.Ddestination_ids:
                if id in outputset:
                    greytaints.add(taint_dict[id])
                    if id in greydependencies:
                        greydependencies[id].add(GreyDependency("D", rtaint.serial_id))
                    else:
                        greydependencies[id] = set([GreyDependency("D", rtaint.serial_id)])
            for id in rtaint.Idestination_ids:
                if id in outputset:
                    greytaints.add(taint_dict[id])
                    if id in greydependencies:
                        greydependencies[id].add(GreyDependency("I", rtaint.serial_id))
                    else:
                        greydependencies[id] = set([GreyDependency("I", rtaint.serial_id)])
            for id in rtaint.Cdestination_ids:
                if id in outputset:
                    greytaints.add(taint_dict[id])
                    if id in greydependencies:
                        greydependencies[id].add(GreyDependency("C", rtaint.serial_id))
                    else:
                        greydependencies[id] = set([GreyDependency("C", rtaint.serial_id)])
        finaltaints = []
        for taint in greytaints:
            if taint.serial_id in greydependencies:
                finaltaints.append(GreyTaint(taint, list(greydependencies[taint.serial_id])))
            else:
                finaltaints.append(GreyTaint(taint, []))
        call.taints = finaltaints
        return call

    # transforms trxn [tx_id] from white box to grey box
    def greybox_trxn(self, tx_id):
        tx = self.DFG[tx_id]
        newcalls = []
        for call in tx.call_level_traces:
            if call.call_tree_path == []:
                rootcall = call
                break
        for call in tx.call_level_traces:
            if call.call_id != rootcall.call_id:
                rootcall.taints.extend(call.taints)
        tx.call_level_traces = [rootcall]
        tx.call_level_traces = [self.greybox_call(tx_id, rootcall.call_id)]

        return tx

if __name__ == "__main__":
    trs = Transformer("traces/", 12345958)
    call = trs.greybox_call(2, 0)
    graph = Graph([call])
    graph.render("%s_%d.gv" % (12345958, 0))
    trxn = trs.greybox_trxn(2)
    graph = Graph(trxn.call_level_traces)
    graph.render("%s_%d.gv" % (12345958, 111))
