import struct
import sys

def read_string(f):
    length = struct.unpack('Q', f.read(8))[0]
    return f.read(length).decode('utf-8')

def read_value(f, type_id):
    if type_id == 0: # UINT8
        return struct.unpack('B', f.read(1))[0]
    if type_id == 1: # INT8
        return struct.unpack('b', f.read(1))[0]
    if type_id == 2: # UINT16
        return struct.unpack('H', f.read(2))[0]
    if type_id == 3: # INT16
        return struct.unpack('h', f.read(2))[0]
    if type_id == 4: # UINT32
        return struct.unpack('I', f.read(4))[0]
    if type_id == 5: # INT32
        return struct.unpack('i', f.read(4))[0]
    if type_id == 6: # FLOAT32
        return struct.unpack('f', f.read(4))[0]
    if type_id == 7: # BOOL
        return struct.unpack('?', f.read(1))[0]
    if type_id == 8: # STRING
        return read_string(f)
    if type_id == 9: # ARRAY
        item_type = struct.unpack('I', f.read(4))[0]
        length = struct.unpack('Q', f.read(8))[0]
        items = []
        for _ in range(length):
            items.append(read_value(f, item_type))
        return items
    if type_id == 10: # UINT64
        return struct.unpack('Q', f.read(8))[0]
    if type_id == 11: # INT64
        return struct.unpack('q', f.read(8))[0]
    if type_id == 12: # FLOAT64
        return struct.unpack('d', f.read(8))[0]
    raise Exception(f"Unknown type {type_id}")

with open(sys.argv[1], 'rb') as f:
    magic = f.read(4)
    if magic != b'GGUF':
        raise Exception("Not a GGUF file")
    version = struct.unpack('I', f.read(4))[0]
    tensors = struct.unpack('Q', f.read(8))[0]
    kv_count = struct.unpack('Q', f.read(8))[0]
    print(f"Version: {version}, Tensors: {tensors}, KV: {kv_count}")
    for _ in range(kv_count):
        try:
            key = read_string(f)
            type_id = struct.unpack('I', f.read(4))[0]
            value = read_value(f, type_id)
            print(f"{key}: {value}")
        except Exception as e:
            print(f"Error reading KV: {e}")
            break
