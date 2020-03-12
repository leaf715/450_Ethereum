import json
import pprint

def parse_int(val):

    if val is not None and val!="" and val!="null":
        val=int(val)
    else:
        val = None
    return val

def parse_bytes(val):
    string=(str(val))[2:]
    l=len(string)
    if l>0:
        if l%2!=0:
            string="0"+string
        try:
            by=bytes.fromhex((string))
            return (by)
        except Exception as e:
            print(e)
    else:
        b="".encode()
        return b


def parse_hexint(val):
    if val is not None and val!="" and val!="null":
        val = int(val[2:], 16)
    else :
        val=None
    return val

def parse_parameter(val):
    temp=val.split("=")
    return temp[0],temp[1]

def parse_dict(val):
    dic={}
    dic1={}
    for i in val:
        v=parse_bytes(i)
        for j in (val.values()):
            for k in j.keys():
                h=parse_bytes(k)
                dic1[h]=j[k]
        dic[v]=dic1
        return dic



class Dependency:
    def __init__(self, val):
        self.parse_from(val)

    def parse_from(self, val):
        # print("===Dependency===")
        P = val.split(" ")
        for i in range(len(P)):
            if len(P[i]) == 0:
                P[i] = None
        while len(P) != 6:
            P.append(None)
        # print(P)
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
        self.Dsource_ids = set([d.source_id for d in self.dependencies if d.type == 'D'])
        self.Isource_ids = set([d.source_id for d in self.dependencies if d.type == 'I'])
        self.Csource_ids = set([d.source_id for d in self.dependencies if d.type == 'C'])
        self.Ddestination_ids = set()
        self.Idestination_ids = set()
        self.Cdestination_ids = set()




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
        if ct["call_tree_path"]!="":
            temp = (ct["call_tree_path"]).split(" ")
            for i in temp :
                self.call_tree_path.append(parse_int(i))
        self.from_address = parse_bytes(ct["from"])
        self.to_address =parse_bytes(ct["to"])
        self.code_address =parse_bytes(ct["code_addr"])
        self.value = ct["value"]
        self.data =parse_bytes(ct["data"])
        self.path =[]
        if ct["call_tree_path"] != "":
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
        self.tx_hash = parse_bytes((tx["tx_hash"]))
        self.gas_price = tx["gas_price"]
        self.origin= parse_bytes(tx["origin"])
        self.storage_written=parse_dict(tx["storage_written"])
        self.call_level_traces = [CallLevelTrace(ct) for ct in tx["call_level_traces"]]
        Ddestinations = {}
        Idestinations = {}
        Cdestinations = {}
        call_trace_dict = {}
        for call in self.call_level_traces:
            Ddestinations[call.call_id] = {}
            Idestinations[call.call_id] = {}
            Cdestinations[call.call_id] = {}
            for taint in call.taints:
                call_trace_dict[taint.serial_id] = call.call_id

        for call in self.call_level_traces:
            for t in call.taints:
                for source_id in t.Dsource_ids:
                    if source_id in call_trace_dict:
                        call_id = call_trace_dict[source_id]
                        if source_id in Ddestinations[call_id]:
                            Ddestinations[call_id][source_id].append(t.serial_id)
                        else:
                            Ddestinations[call_id][source_id] = [t.serial_id]
                for source_id in t.Isource_ids:
                    for source_id in t.Isource_ids:
                        if source_id in call_trace_dict:
                            call_id = call_trace_dict[source_id]
                            if source_id in Idestinations[call_id]:
                                Idestinations[call_id][source_id].append(t.serial_id)
                            else:
                                Idestinations[call_id][source_id] = [t.serial_id]
                for source_id in t.Csource_ids:
                    for source_id in t.Csource_ids:
                        if source_id in call_trace_dict:
                            call_id = call_trace_dict[source_id]
                            if source_id in Cdestinations[call_id]:
                                Cdestinations[call_id][source_id].append(t.serial_id)
                            else:
                                Cdestinations[call_id][source_id] = [t.serial_id]
        for call in self.call_level_traces:
            for t in call.taints:
                if t.serial_id in Ddestinations[call.call_id]:
                    t.Ddestination_ids = set(Ddestinations[call.call_id][t.serial_id])
                if t.serial_id in Idestinations[call.call_id]:
                    t.Idestination_ids = set(Idestinations[call.call_id][t.serial_id])
                if t.serial_id in Cdestinations[call.call_id]:
                    t.Cdestination_ids = set(Cdestinations[call.call_id][t.serial_id])


def parse_file(file_name):
    with open(file_name, "r") as f:
        data = json.load(f)
        # print(data)
        # for tx in data:
        #     print(tx)
        #     print("Ok")
    transactions=[TransactionLevelTrace(tx) for tx in data]
    return transactions


def test(file_name):
    from struct_dump import _pprint
    assert file_name[-5:] == ".json"
    _pprint(parse_file(file_name))


if __name__ == "__main__":
    test("traces/12345k/12345678.json")
