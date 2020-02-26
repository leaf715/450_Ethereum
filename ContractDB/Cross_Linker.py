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

# storage_written: is a dict which summarizes how this transaction overwrites the storage.
# o key: is a byte string, the address of the contract.
# o value: is a dict, the places where the contract’s storage is overwritten.
# ▪ key: is a byte string, the location of a storage slot.
# ▪ value: is an integer which equals to the serial_id of the taint corresponding to
# the data finally written to this slot.

# Storage-write log. Physically, they can be stored in a single file or in separate files / folders, but
# logically the storage-write log is a single file consisting of multiple lines, each line being a “storage
# write record”. A record has 3 columns:
# o Slot location (byte string): the slot being written. This information can be found in the
# storage_written field of a transaction-level trace.
# o Block number (int).
# o Transaction index (int)

    def link(self, trace, tx_id, direction):
        path = self.get_trace(self.num_str8(trace))

        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                tx = data[tx_id]
            if direction == "forward":
                linked_dict = {}
                print(json.dumps(data, indent=2))
            elif direction == "backward":
                linked_dict = {}
                for call in tx["call_level_traces"]:
                    for taint in call["taints"]:
                        taint_info = taint.split(" | ")[0].split(" ")
                        serial_id = taint_info[0]
                        deps = [dep.split(" ") for dep in taint.split(" | ")[1:]]
                        if taint_info[2] == "SLOAD":
                            for dep in deps:
                                if dep[1] == "-6":
                                    loc = call["to"]
                                    storage_path = self.get_state_folder(loc)+"storage-write.log"
                                    if os.path.exists(storage_path): #check sw.log of contract to find last trxn that writes to it
                                        f_sw = open(storage_path, "r")
                                        store = f_sw.readline().strip().split(" ")
                                        print(store)
                                        slot = store[0]
                                        last_block = store[1]
                                        last_trxn = store[2]
                                        linked_path = self.get_trace(last_block) #find trxn that wrote to contract last
                                        if os.path.exists(path):
                                            with open(path, "r") as f:
                                                linked_data = json.load(f)
                                                linked_tx = linked_data[int(last_trxn)]
                                            if loc in linked_tx["storage_written"]: #find taint id of writing trxn that wrote to slot in contract
                                                if slot in linked_tx["storage_written"][loc]:
                                                    linked_dict[serial_id] = [int(last_block), int(last_trxn), linked_tx["storage_written"][loc][slot]]
                                    break
            return linked_dict





if __name__ == "__main__":
    CL = Cross_Linker("State_DB/", "traces/", 2)
    print(CL.link(12345702, 0, "backward"))
