import json
import os
import glob
import shutil

class Cross_Linker:
    def __init__(self, log_dir, trace_dir, level_size):
        if not os.path.isdir(log_dir):
            error("no such log directory")
        if not os.path.isdir(trace_dir):
            error("no such trace directory")
        self.log_dir = log_dir
        self.trace_dir = trace_dir
        self.level_size = level_size

    def get_trace(self, i):
        return self.trace_dir+i[:5]+"k/"+i+".json"

    def get_state_folder(self, bytestr):
        return self.log_dir+bytestr[:2+self.level_size]+"/"+bytestr[:2+2*self.level_size]+"/"+bytestr[:2+3*self.level_size]+"/"+bytestr+"/"

    def num_str8(self, i):
        num_str = str(i)
        return "0"*(8-len(num_str))+num_str

    def get_latest(self, stores, trace, tx_id):
        i = 0
        while i < len(stores):
            store = stores[i].strip().split(" ")
            if int(store[1]) == trace:
                if int(store[2]) >= tx_id:
                    break
            if int(store[1]) > trace:
                break;
            i+=1
        if i == len(stores):
            return stores[-1].strip().split(" ")
        i-=1
        if i < 0:
            return None
        store = stores[i].strip().split(" ")
        return store

    def get_next(self, stores, trace, slot, tx_id):
        i = 0
        while i < len(stores):
            store = stores[i].strip().split(" ")
            if store[0] == slot:
                if int(store[1]) == trace:
                    if int(store[2]) > tx_id:
                        break
                if int(store[1]) > trace:
                    break;
            i+=1
        if i == len(stores):
            return [math.inf,math.inf]
        time = stores[i].split(" ")
        return [int(store[1]), int(store[2])]

    def link(self, trace, tx_id, direction):
        path = self.get_trace(self.num_str8(trace))
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                tx = data[tx_id]
            if direction == "forward":
                contract_dict = {}
                for loc in tx["storage_written"].keys():
                    linked_dict = {}
                    for slot in tx["storage_written"][loc].keys():
                        # print("checking contract "+loc+" slot "+slot)
                        serial_id = tx["storage_written"][loc][slot]
                        linked_taints = set()
                        storage_path = self.get_state_folder(loc)+"storage-write.log"
                        if os.path.exists(storage_path):
                            # print("SW found "+ storage_path)
                            f_sw = open(storage_path, "r")
                            stores = f_sw.readlines()
                            timeframe = [[trace, tx_id], self.get_next(stores, trace, slot, tx_id)]
                            call_path = self.get_state_folder(loc)+"call.log"
                            if os.path.exists(call_path):
                                # print("Calls found "+call_path)
                                # print(timeframe)
                                f_call = open(call_path, "r")
                                calls = f_call.readlines()
                                i = 0
                                call = calls[i].strip().split(" ")
                                while int(call[0]) < timeframe[0][0] or (int(call[0]) == timeframe[0][0] and int(call[1]) < timeframe[0][1]):
                                    i+=1
                                    call = calls[i].strip().split(" ")
                                while int(call[0]) < timeframe[1][0] or (int(call[0]) == timeframe[1][0] and int(call[1]) < timeframe[1][1]):
                                    linked_path = self.get_trace(call[0])
                                    if os.path.exists(linked_path):
                                        with open(linked_path, "r") as f:
                                            linked_data = json.load(f)
                                            linked_tx = linked_data[int(call[1])]
                                            linked_call = linked_tx["call_level_traces"][int(call[2])]
                                        for taint in linked_call["taints"]:
                                            taint_info = taint.split(" | ")[0].split(" ")
                                            taint_serial_id = taint_info[0]
                                            deps = [dep.split(" ") for dep in taint.split(" | ")[1:]]
                                            if taint_info[2] == "SLOAD":
                                                for dep in deps:
                                                    if dep[1] == "-6":
                                                        linked_taints.add((int(call[0]), int(call[1]), int(taint_serial_id)))
                                                        break
                                    i+=1
                                    call = calls[i].strip().split(" ")
                        linked_dict[serial_id] = linked_taints
                    contract_dict[loc] = linked_dict
            elif direction == "backward":
                # print("backwards")
                linked_dict = {}
                for call in tx["call_level_traces"]:
                    for taint in call["taints"]:
                        taint_info = taint.split(" | ")[0].split(" ")
                        serial_id = int(taint_info[0])
                        deps = [dep.split(" ") for dep in taint.split(" | ")[1:]]
                        if taint_info[2] == "SLOAD":
                            # print("SLOAD found")
                            for dep in deps:
                                if dep[1] == "-6":
                                    loc = call["to"]
                                    storage_path = self.get_state_folder(loc)+"storage-write.log"
                                    if os.path.exists(storage_path): #check sw.log of contract to find last trxn that writes to it
                                        # print("SW log found "+storage_path)
                                        f_sw = open(storage_path, "r")
                                        stores = f_sw.readlines()
                                        store = self.get_latest(stores, trace, tx_id)
                                        if store:
                                            # print(store)
                                            slot = store[0]
                                            last_block = store[1]
                                            last_trxn = store[2]
                                            linked_path = self.get_trace(last_block)
                                            if os.path.exists(linked_path):
                                                # print("linked TX found "+linked_path)
                                                with open(linked_path, "r") as f:
                                                    linked_data = json.load(f)
                                                    linked_tx = linked_data[int(last_trxn)]
                                                if loc in linked_tx["storage_written"]: #find taint id of writing trxn that wrote to slot in contract
                                                    if slot in linked_tx["storage_written"][loc]:
                                                        linked_dict[serial_id] = [int(last_block), int(last_trxn), linked_tx["storage_written"][loc][slot]]
                                    break
            return linked_dict





if __name__ == "__main__":
    CL = Cross_Linker("State_DB/", "traces/", 2)
    print(CL.link(12345701, 0, "backward"))
    print(CL.link(12345678, 0, "forward"))
