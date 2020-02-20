import json
import os
import glob
import shutil

log_dir = "State_DB/"
contracts = []

def get_traces(dir):
    files = sorted([f for f in os.listdir(dir)])
    return files

def get_folder(bytestr):
    folder = log_dir+bytestr
    if not os.path.isdir(folder):
        os.mkdir(folder)
    return folder

def build_DB(restart, trace_dir):
    if restart:
        files = glob.glob(log_dir+'*')
        for f in files:
            shutil.rmtree(f)
        f_read = open("files_read.log", "w+")
    else:
        f_read = open("files_read.log", "r+")

    f_dir = open("dir.log", "a+")

    contracts = f_dir.readlines()
    # f_meta = open(log_dir+"metadata.log", "a")
    # f_call = open(log_dir+"call.log", "a")
    # f_sw = open(log_dir+"storage-write.log", "a")

    traces = get_traces(trace_dir)
    print(traces)
    if not restart:
        f_read.seek(0)
        last = f_read.readline()
        if last:
            i = 0
            while i < len(traces) and traces[i][:-5] != last:
                i+=1
            traces = traces[i:]
    print(traces)
    while traces:
        trace = traces.pop(0)
        with open(trace_dir+trace, "r") as f:
            data = json.load(f)
        for tx in data:
            block_number = str(tx["block_number"])
            trxn_id = str(tx["tx_index"])
            for call in tx["call_level_traces"]:
                call_id = str(call["call_id"])
                if call["call_type"] == "CREATE" or call["call_type"] == "CREATE2" and call["success"]:
                    bytestr = call["outputs"][-1]
                    contract_folder = get_folder(bytstr.split("data=0x", 1)[1])
                    f_meta = open(contract_folder+"/metadata.log", "a")
                    f_meta.write(bytstr + " " + block_number + " " + trxn_id + " " + call_id + "\n")
                    f_meta.close()
                    f_dir.write(bytestr+"\n")
                    contracts.append(bytestr)
                output_opcodes = [code.split(" ", 1)[0] for code in call["outputs"]]
                if "SELFDESTRUCT" in output_opcodes and call["success"]:
                    contract_folder = get_folder(call["to"])
                    f_meta = open(contract_folder+"/metadata.log", "a")
                    f_meta.write(block_number + " " + trxn_id + " " + call_id + "\n")
                    f_meta.close()
                if call["to"] in contracts:
                    contract_folder = get_folder(call["to"])
                    f_call = open(contract_folder+"/call.log", "a")
                    f_call.write(block_number + " " + trxn_id + " " + call_id + "\n")
                    f_call.close()
            for bytestr in tx["storage_written"]:
                contract_folder = get_folder(bytestr)
                f_sw = open(contract_folder+"/storage-write.log", "a")
                for slot in tx["storage_written"][bytestr]:
                    f_sw.write(slot + " " + block_number + " " + trxn_id + "\n")
                f_sw.close()
        f_read.seek(0)
        f_read.write(trace[:-5]+"\n")


if __name__ == "__main__":
    build_DB(True, "traces/")
