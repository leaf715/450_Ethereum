import json
import pprint

def parse_int(val):
    if val is not None and val!="" and val!="null":
        val=int(val)
    return val

def parse_bytes(val):
    by=val.encode()
    return (by)

def parse_hexint(val):
    if val is not None and val!="" and val!="null":
        val = int(val[2:], 16)
    return val

def parse_parameter(val):
    temp=val.split("=")
    return temp[0],temp[1]


class Dependency:
    def __init__(self, val):
        self.parse_from(val)

    def parse_from(self, val):
        # print("===Dependency===")
        P = val.split(" ")

        if len(P) == 3:
            for i in range(0,3):
                P.append(None)

        self.type=P[0]
        self.source_id=parse_int(P[1])
        self.name=P[2]
        self.offset=parse_hexint(P[3])
        self.source_offset=parse_hexint(P[4])
        self.length=parse_hexint(P[5])

class Taint:
    def __init__(self, string):
        self.parse_from(string)

    def parse_from(self, string):
        # print("======Taints=====")
        R = string.split(" | ")
        T = R[0].split(" ")
        self.serial_id=parse_int(T[0])
        self.pc=parse_int(T[1])
        self.name=T[2]
        self.value=parse_bytes(T[3])
        self.dependencies=[Dependency(r) for r in R[1:]]





class Output:
    def __init__(self, out):
        self.parse_from(out)

    def parse_from(self, out):
        # print("===Output===")
        t=out.split(" ")
        self.name=t[0]
        self.trigger_id=int(t[1])
        self.parameters={}
        for T in t[2:]:
            key,val=parse_parameter(T)
            self.parameters[key]=parse_bytes(val)

class CallLevelTrace:
    def __init__(self, ct):
        self.parse_from(ct)

    def parse_from(self, ct):
        # print("===Call Trace===")
        self.success = ct["success"]
        self.error_message = ct["error_message"]
        self.call_type = ct["call_type"]
        self.call_id = ct["call_id"]
        self.call_tree_path=[]
        temp = (ct["call_tree_path"]).split(" ")
        for i in temp:
            self.call_tree_path.append(parse_int(i))
        self.from_address = parse_bytes(ct["from"])
        self.to_address =parse_bytes(ct["to"])
        self.code_address =parse_bytes(ct["code_addr"])
        self.value = ct["value"]
        self.data =parse_bytes(ct["data"])
        self.path =[]
        temp = (ct["path"]).split(" ")
        for i in temp:
            self.path.append(parse_int(i))
        self.outputs = [Output(out) for out in ct["outputs"]]
        self.taints = [Taint(taint) for taint in ct["taints"]]



class TransactionLevelTrace:
    def __init__(self, tx):
        self.parse_from(tx)

    def parse_from(self, tx):
        self.block_number = tx["block_number"]
        self.tx_index = tx["tx_index"]
        self.tx_hash = parse_bytes(str(tx["tx_hash"]))
        self.gas_price = tx["gas_price"]
        self.origin= parse_bytes(tx["origin"])
        self.storage_written=tx["storage_written"]
        self.call_traces = [CallLevelTrace(ct) for ct in tx["call_level_traces"]]


def parse_file(file_name):
    with open(file_name, "r") as f:
        data = json.load(f)

    transactions=[TransactionLevelTrace(tx) for tx in data]
    return transactions


# def test(file_name):
#     from struct_dump import _pprint
#     assert file_name[-5:] == ".json"
#     _pprint(parse_file(file_name))


if __name__ == "__main__":
    parse_file("./12345678.json")

