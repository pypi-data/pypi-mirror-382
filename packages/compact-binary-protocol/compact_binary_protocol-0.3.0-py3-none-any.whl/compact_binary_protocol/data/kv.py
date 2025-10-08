import struct
from ..encodings import encode_var_string
from .constants import TYPE_KV

class DataKv:
    """
    Generic key/value pairs sensor-data item.

    - sensor_type: TYPE_KV
    - sensor_version: 1
    - payload:
        - count: u8
        - repeat count times: key VarString, value VarString (ASCII)
    All keys and values are encoded as strings.
    """
    def __init__(self, kv_pairs=None):
        self.sensor_type = TYPE_KV
        self.sensor_version = 1
        # Normalize input to list[tuple[str,str]]
        pairs_list = []
        if kv_pairs is None:
            items = []
        elif isinstance(kv_pairs, dict):
            items = list(kv_pairs.items())
        else:
            items = list(kv_pairs)
        for k, v in items:
            if k is None:
                continue
            ks = str(k)
            vs = '' if v is None else str(v)
            pairs_list.append((ks, vs))
        self.pairs = pairs_list

    def to_bytes(self) -> bytes:
        # Build payload: count + VarString pairs
        count = len(self.pairs)
        payload = struct.pack('>B', count)
        for k, v in self.pairs:
            payload += encode_var_string(k)
            payload += encode_var_string(v)
        # Prepend SensorData header (type, version, length)
        header = struct.pack('>BBH', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self) -> str:
        items = ', '.join(f"{k}={v}" for k, v in self.pairs)
        return f"Kv(type={self.sensor_type}, ver={self.sensor_version}, {items})"
