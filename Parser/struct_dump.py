import json

def _struct_to_json(struct):
    if struct is None:
        return None
    if type(struct) in [int, float, bool, str]:
        return struct
    if type(struct) is bytes:
        return {
            "__class__": str(struct.__class__),
            "hex()": struct.hex()
        }            
    if type(struct) is list:
        return [_struct_to_json(x) for x in struct]
    if type(struct) is dict:
        d = {}
        for key in struct:
            key_str = key if type(key) is str else "%s %s" % (type(key), key.hex() if type(key) is bytes else key)
            d[key_str] = _struct_to_json(struct[key])
        return d
    if type(struct) in [tuple, set]:
        return {
            "__class__": str(struct.__class__),
            "": [_struct_to_json(x) for x in struct]
        }
    # else, complicated class
    d = {"__class__": str(struct.__class__)}
    for key in struct.__dict__:
        d[key] = _struct_to_json(struct.__dict__[key])
    return d

def _pretty_json(obj):
    return json.dumps(obj, indent=2, sort_keys=False)

def _pprint(struct):
    print(_pretty_json(_struct_to_json(struct)))
