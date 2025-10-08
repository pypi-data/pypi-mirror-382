import struct
from .base import Packet
from ..encodings import encode_var_string

class ConfigPacket(Packet):
    """
    Configuration packet using key/value pairs.
    Body format:
      - pair_count: 1 byte (u8)
      - pairs: repeat pair_count times
          - key: VarString (ASCII)
          - value: VarString (ASCII)
    All keys and values are strings.
    """
    def __init__(self, imei, kv_pairs, transaction_id=0):
        super().__init__('C', imei, transaction_id)
        # Normalize to list of (key, value) tuples with str types
        if isinstance(kv_pairs, dict):
            items = list(kv_pairs.items())
        else:
            items = list(kv_pairs or [])
        norm = []
        for k, v in items:
            if k is None:
                continue
            ks = str(k)
            vs = '' if v is None else str(v)
            norm.append((ks, vs))
        self.pairs = norm

    def to_bytes(self):
        header = self.build_header()
        count = len(self.pairs)
        body = struct.pack('>B', count)
        for k, v in self.pairs:
            body += encode_var_string(k)
            body += encode_var_string(v)
        return header + body

    @staticmethod
    def decode(imei: str, transaction_id: int, data: bytes):
        from ..decoders import DataReader
        reader = DataReader(data)
        if len(data) == 0:
            count = 0
        else:
            reader.read_u8()
            reader.read_data_item_header()
            count = reader.read_u8()
        pairs = []
        for _ in range(count):
            key = reader.read_var_string()
            value = reader.read_var_string()
            pairs.append((key, value))
        return ConfigPacket(imei, pairs, transaction_id)

    def to_dict(self):
        d = {}
        for k, v in self.pairs:
            d[k] = v
        return d

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        for k, v in self.pairs:
            print(f"  {k}: {v}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)