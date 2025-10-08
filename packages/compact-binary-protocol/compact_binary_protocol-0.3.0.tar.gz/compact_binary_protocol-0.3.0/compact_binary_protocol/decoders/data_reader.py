class DataReader:
    """Sequential reader for bytes with big-endian decode helpers.

    Extended to support parsing Telemetry data items and KV payloads used
    for configuration replies (Telemetry with a single DataKv item).
    """

    def __init__(self, data):
        self.data = data
        self.position = 0

    # ---- Primitive readers ----
    def remaining(self) -> int:
        return max(0, len(self.data) - self.position)

    def read_u8(self) -> int:
        if self.position + 1 > len(self.data):
            raise IndexError("Not enough data to read u8")
        val = self.data[self.position]
        self.position += 1
        return val

    def read_u16(self) -> int:
        if self.position + 2 > len(self.data):
            raise IndexError("Not enough data to read u16")
        val = int.from_bytes(self.data[self.position:self.position+2], 'big')
        self.position += 2
        return val

    def read_bytes(self, n: int) -> bytes:
        if self.position + n > len(self.data):
            raise IndexError(f"Not enough data to read {n} bytes")
        b = self.data[self.position:self.position+n]
        self.position += n
        return b

    def read_var_string(self):
        if self.position >= len(self.data):
            raise IndexError("Not enough data to read string length")
        length = self.data[self.position]
        self.position += 1
        if self.position + length > len(self.data):
            raise IndexError(f"Not enough data to read string of length {length}")
        string_bytes = self.data[self.position:self.position + length]
        self.position += length
        return string_bytes.decode('ascii')

    def read_int4(self):
        if self.position + 4 > len(self.data):
            raise IndexError("Not enough data to read 4-byte integer")
        int_bytes = self.data[self.position:self.position + 4]
        self.position += 4
        return int.from_bytes(int_bytes, byteorder='big')

    # ---- Data item parsing helpers ----
    def read_data_item_header(self):
        """Read a Data item header [type u8][version u8][length u16].
        Returns (dtype, dver, length).
        """
        dtype = self.read_u8()
        dver = self.read_u8()
        dlen = self.read_u16()
        return dtype, dver, dlen

    def read_data_item(self):
        """Read a single Data item and return (dtype, dver, payload_bytes)."""
        dtype, dver, dlen = self.read_data_item_header()
        payload = self.read_bytes(dlen)
        return dtype, dver, payload

    def read_data_items(self):
        """Read Telemetry body formatted as [count u8][items...].
        Returns a list of tuples (dtype, dver, payload_bytes).
        """
        items = []
        if self.remaining() <= 0:
            return items
        count = self.read_u8()
        for _ in range(count):
            items.append(self.read_data_item())
        return items

    # ---- KV decoding helpers ----
    @staticmethod
    def parse_kv_payload(payload: bytes):
        """Parse a DataKv payload (count + key/value VarStrings).
        Returns a list of (key, value) tuples.
        """
        r = DataReader(payload)
        pairs = []
        try:
            cnt = r.read_u8() if r.remaining() > 0 else 0
            for _ in range(cnt):
                k = r.read_var_string()
                v = r.read_var_string()
                pairs.append((k, v))
        except IndexError:
            # Truncate on malformed payload
            pass
        return pairs

    @staticmethod
    def kv_pairs_to_dict(pairs):
        d = {}
        for k, v in pairs:
            d[k] = v
        return d
