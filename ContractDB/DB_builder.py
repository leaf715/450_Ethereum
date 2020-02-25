import json
import os
import glob
import shutil

class DB_Builder:
    def __init__(self, log_dir, level_size):
        if not os.path.isdir(log_dir):
            os.mkdir(log_dir)
        self.log_dir = log_dir
        self.level_size = level_size

    def get_trace(self, dir, i):
        return dir+i+".json"

    def num_str8(self, i):
        num_str = str(i)
        return "0"*(8-len(num_str))+num_str

    def get_folder(self, bytestr):
        folder = self.log_dir+bytestr[:2+self.level_size]
        if not os.path.isdir(folder):
            os.mkdir(folder)
        folder = self.log_dir+bytestr[:2+self.level_size]+"/"+bytestr[:2+2*self.level_size]
        if not os.path.isdir(folder):
            os.mkdir(folder)
        folder = self.log_dir+bytestr[:2+self.level_size]+"/"+bytestr[:2+2*self.level_size]+"/"+bytestr[:2+3*self.level_size]
        if not os.path.isdir(folder):
            os.mkdir(folder)
        folder = self.log_dir+bytestr[:2+self.level_size]+"/"+bytestr[:2+2*self.level_size]+"/"+bytestr[:2+3*self.level_size]+"/"+bytestr
        if not os.path.isdir(folder):
            os.mkdir(folder)
        return folder

    def build_DB(self, trace_dir, start, end, restart = None):

        if restart:
            shutil.rmtree(self.log_dir)
            os.mkdir(self.log_dir)
            f_read = open(self.log_dir+"last_read.log", "w+")
        else:
            f_read = open(self.log_dir+"last_read.log", "r+")

        if restart:
            trace = start
        else:
            f_read.seek(0)
            trace = int(f_read.readline())+1


        while trace <= end:
            print(trace)
            path = self.get_trace(trace_dir, self.num_str8(trace))
            if os.path.exists(path):
                with open(self.get_trace(trace_dir, self.num_str8(trace)), "r") as f:
                    data = json.load(f)
                for tx in data:
                    block_number = str(tx["block_number"])
                    trxn_id = str(tx["tx_index"])
                    for call in tx["call_level_traces"]:
                        call_id = str(call["call_id"])
                        if (call["call_type"] == "CREATE" or call["call_type"] == "CREATE2") and call["success"]:
                            bytestr = call["outputs"][-1]
                            contract_folder = self.get_folder(bytestr.split("data=0x", 1)[1])
                            f_meta = open(contract_folder+"/metadata.log", "a")
                            f_meta.write(bytestr + " " + block_number + " " + trxn_id + " " + call_id + "\n")
                            f_meta.close()
                        output_opcodes = [code.split(" ", 1)[0] for code in call["outputs"]]
                        if "SELFDESTRUCT" in output_opcodes and call["success"]:
                            contract_folder = self.get_folder(call["to"])
                            f_meta = open(contract_folder+"/metadata.log", "a")
                            f_meta.write(block_number + " " + trxn_id + " " + call_id + "\n")
                            f_meta.close()
                        if call["call_type"] in ["CALL", "STATICCALL"]: #Deal with other call types
                            contract_folder = self.get_folder(call["to"])
                            f_call = open(contract_folder+"/call.log", "a")
                            f_call.write(block_number + " " + trxn_id + " " + call_id + "\n")
                            f_call.close()
                        if call["call_type"] in ["DELEGATECALL", "CALLCODE"]: #Deal with other call types
                            contract_folder = self.get_folder(call["from"])
                            f_call = open(contract_folder+"/call.log", "a")
                            f_call.write(block_number + " " + trxn_id + " " + call_id + "\n")
                            f_call.close()
                    for bytestr in tx["storage_written"].keys():
                        contract_folder = self.get_folder(bytestr)
                        f_sw = open(contract_folder+"/storage-write.log", "a")
                        for slot in tx["storage_written"][bytestr].keys():
                            f_sw.write(slot + " " + block_number + " " + str(tx["storage_written"][bytestr][slot]) + "\n")
                        f_sw.close()
            f_read.seek(0)
            f_read.write(self.num_str8(trace)+"\n")
            trace+=1


if __name__ == "__main__":
    DB = DB_Builder("State_DB/", 2)
    DB.build_DB("traces/", 12345670, 12345700, True)
