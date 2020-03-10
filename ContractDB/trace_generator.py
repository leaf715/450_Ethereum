import json
import os
import glob
import shutil
import random

null = None
output_options = ["SSTORE", "SSTORE", "SSTORE", "SSTORE", "SSTORE", "CALL", "CALLCODE", "SELFDESTRUCT"]
contract1 = ["0xabcd", "0xabde", "0xaede", "0xa13e", "0xa13e", "0xa13e"]
contract2 = [hex(random.randint(268435456, 4294967295))[2:]+hex(random.randint(268435456, 4294967295))[2:] for i in range(6)]
for i in range(3):
    contract2.append(contract2[0])
    contract2.append(contract2[1])

def num_str8(i):
    num_str = str(i)
    return "0"*(8-len(num_str))+num_str

def rand_trxn():
    return hex(random.randint(268435456, 4294967295))+hex(random.randint(268435456, 4294967295))[2:]+hex(random.randint(268435456, 4294967295))[2:]+hex(random.randint(268435456, 4294967295))[2:]

def rand_bytestring():
    return random.choice(contract1) + random.choice(contract2)

def create_call(call_id, call_code, caller, caller_id, to_code):
    call = {}
    new_call = []
    success = random.randint(0,10) > 3
    call["success"] = success
    if call["success"]:
        call["error_message"] = null
    else:
        call["error_message"] = "unknown error"
    call["call_type"] = call_code
    call["call_id"] = call_id
    call["call_tree_path"] = str(caller_id)
    call["from"] = caller
    call["to"] = to_code
    call["code_addr"] = call["to"]
    if call["success"]:
        call["value"] = random.randint(0,1000)*10
        call["data"] = rand_bytestring()
    else:
        call["value"] = 0
        call["data"] = "0x"
    taints =  ["0 42 _PUSHED 0x | D -1 x"]
    taintcount = 1
    for i in range(random.randint(0,3)):
        taintcount+=1
        taints.append(str(i+1)+" 42 SLOAD 0x | I 0 loc | D -6 data")
    call["taints"] = taints
    if not call["success"]:
        call["outputs"] = []
    elif call_code in ["CREATE", "CREATE2"]:
        new_contract = rand_bytestring()
        call["outputs"] = ["RETURN 0 data="+new_contract]
    else:
        outputs = []
        output_line = ""
        for i in range(random.randint(0,4)):
            output_code = random.choice(output_options)
            output_line = output_code
            if output_code == "SELFDESTRUCT":
                output_line = "SELFDESTRUCT 42 address="+to_code
                outputs.append(output_line)
                break
            if output_code == "CALL":
                to_addr = rand_bytestring()
                output_line = "CALL "+ str(taintcount) +" gas=0x0 to="+to_addr
                outputs.append(output_line)
                taints.append(str(taintcount)  + " 43 CALL 0x | I 0 loc | D " + str(taintcount-1) +" data")
                taintcount+=1
                new_call.append(["CALL", call["to"], call_id, to_addr])
            if output_code == "CALLCODE":
                to_addr = rand_bytestring()
                output_line = "CALLCODE "+ str(taintcount) +" gas=0x0 to="+to_addr
                outputs.append(output_line)
                taints.append(str(taintcount)  + " 43 CALLCODE 0x | I 0 loc | D " + str(taintcount-1) +" data")
                taintcount+=1
                new_call.append(["CALLCODE", call["to"], call_id, to_addr])
            if output_code == "SSTORE":
                output_line = "SSTORE " + str(taintcount) + " loc=" + call["to"] + " data=" + rand_bytestring()
                taints.append(str(taintcount)  + " 43 SSTORE 0x | I 0 loc | D " + str(taintcount-1) +" data")
                taintcount+=1
                outputs.append(output_line)
        call["taints"] = taints
        call["outputs"] = outputs

    return call, new_call

def gen_traces(start, stop, trace_dir):
    if not os.path.isdir(trace_dir):
        os.mkdir(trace_dir)
    for block in range(start, stop+1):
        trxns = []
        for tx in range(random.randint(1, 3)):
            trxn = {}
            trxn["block_number"] = block
            trxn["tx_index"] = tx
            trxn["tx_hash"] = rand_trxn()
            trxn["gas_price"] = random.randint(100,1000)*10
            trxn["origin"] = rand_bytestring()
            caller = trxn["origin"]
            calls = []
            call_id = 0
            call_code = random.choice(["CALL", "CALL", "CALL", "CALL", "CALL", "CALL", "CREATE", "CREATE2"])
            call, more_calls = create_call(call_id, call_code, caller, "", rand_bytestring())
            calls.append(call)
            call_id = 1
            while more_calls:
                new_call = more_calls.pop(0)
                call, more_more_calls = create_call(call_id, new_call[0], new_call[1], new_call[2], new_call[3])
                calls.append(call)
                more_calls = more_calls + more_more_calls
                call_id+=1

            trxn["call_level_traces"] = calls
            storage = {}
            for call in calls:
                for output in call["outputs"]:
                    parsed = output.split(" ")
                    if parsed[0] == "SSTORE":
                        if parsed[2][4:] in storage:
                            dict = storage[parsed[2][4:]]
                            dict[parsed[3][5:]] = int(parsed[1])
                            storage[parsed[2][4:]] = dict
                        else:
                            storage[parsed[2][4:]] = {parsed[3][5:]: int(parsed[1])}
            trxn["storage_written"] = storage
            trxns.append(trxn)
        trace_folder = trace_dir+num_str8(block)[:5]+"k/"
        if not os.path.isdir(trace_folder):
            os.mkdir(trace_folder)
        with open(trace_folder+num_str8(block)+".json", "w") as f:
            f.write(json.dumps(trxns, indent=2))

if __name__ == "__main__":
    trace_dir = "traces/"
    gen_traces(12345680, 12345700,trace_dir)
