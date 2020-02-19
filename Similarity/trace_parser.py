import json

class ArgumentSegmentProperty:
    def __init__(self, string):
        self.offset = None # optional field
        self.bitmap = None 
        self.dfg_node_id = None # NOTE that this is NULLABLE!!
        self.parse_from(string)

    def parse_from(self, string):
        z = string.split(":")
        if len(z) == 2: # there is offset
            self.offset = z[0]
        y = z[-1].split("@")
        if len(y) < 2: return ## const-pad field
        self.bitmap = y[0]
        self.dfg_node_id = int(y[1])


class EventArgument:
    def __init__(self, string):
        self.name = None
        self.value = None # a 0x-string
        self.segments = []
        self.parse_from(string)

    def parse_from(self, string):
        self.name, rest = string.split("=")
        z = rest.split("(")
        self.value = z[0]
        if len(z) == 1: # there is no braket
            return
        segment_strings = z[1][:-1].split(",")
        for segment_string in segment_strings:
            if len(segment_string) == 0: # empty string
                return
            self.segments.append(ArgumentSegmentProperty(segment_string))


class Event:
    def __init__(self, string):
        self.event_id = None
        self.pc = None
        self.name = None
        self.flags = None
        self.arguments = []
        self.parse_from(string)

    def parse_flags(self):
        if len(self.flags) == 2:
            self.flags = [] # empty
        else:
            self.flags = [ (int(x.split(":")[0]), x.split(":")[1]) for x in self.flags[1:-2].split(",") ]

    def parse_from(self, string):
        args = string.split(" ")
        #
        self.event_id = int(args[0])
        self.pc = int(args[1])
        self.name = args[2]
        # fix: JUMPI[*]
        if self.name[:5] == "JUMPI":
            self.name = "JUMPI"
        # end fix
        self.flags = args[3]
        self.parse_flags()
        #
        argument_strings = args[4:]
        for argument_string in argument_strings:
            self.arguments.append(EventArgument(argument_string))


class PlainNode:
    def __init__(self, string):
        self.node_id = None
        self.call_nonce = None
        self.name = None
        self.extra_info = []
        self.source_node_ids = []
        self.parse_from(string)

    def parse_from(self, string):
        args = string.split(" ")
        self.node_id = int(args[0])
        self.call_nonce = int(args[1])
        body = args[2]
        # parse the body
        left, right = body.split("(")
        z = left.split("_")
        self.name = z[0]
        self.extra_info = z[1:]
        self.source_node_ids = [ int(x) for x in right.split(",")[:-1] ]


class CallTrace:
    def __init__(self, ct):
        self.parse_from(ct)

    def parse_from(self, ct):
        self.success = ct["success"]
        self.code = ct["code"]
        self.call_type = ct["call_type"]
        self.call_nonce = ct["call_nonce"]
        self.call_chain = eval(ct["cti"])
        self.from_address = ct["from"]
        self.to_address = ct["to"]
        self.code_address = ct["code_addr"]
        self.value = ct["value"]
        self.data = ct["data"]
        self.path = eval(ct["path"])
        self.events = [Event(e) for e in ct["events"]]


class Transaction:
    def __init__(self, tx):
        self.parse_from(tx)

    def parse_from(self, tx):
        self.block_number = tx["block_number"]
        self.tx_index = tx["tx_index"]
        self.tx_hash = tx["tx_hash"]
        self.gas_price = tx["gas_price"]
        self.call_traces = [CallTrace(ct) for ct in tx["call_traces"]]
        self.plain_nodes = [PlainNode(n) for n in tx["expr_graph"]]


def parse_file(file_name):
    with open(file_name, "r") as f:
        data = json.load(f)
    transactions = [Transaction(tx) for tx in data]
    return transactions


def test(file_name):
    from struct_dump import _pprint
    assert file_name[-5:] == ".json"
    _pprint(parse_file(file_name))

if __name__ == "__main__":
    test("./04501736.json")
    
# $ python3 trace_parser.py > test_parser.json