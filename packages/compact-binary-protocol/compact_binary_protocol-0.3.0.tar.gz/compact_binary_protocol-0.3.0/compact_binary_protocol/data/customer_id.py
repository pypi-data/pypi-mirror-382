import struct
from .constants import TYPE_CUSTOMER_ID

class DataCustomerId:
    """
    SensorData to carry the Customer ID bytes.

    - sensor_type: 11
    - sensor_version: 1
    - payload: VarBytes (len:uint8 + raw bytes)

    Accepts a hex string (even-length, optional 0x prefix) or bytes/bytearray.
    """
    def __init__(self, customer_id):
        self.sensor_type = TYPE_CUSTOMER_ID
        self.sensor_version = 1
        self._raw = b""
        # Normalize to raw bytes similar to previous PowerOnPacket handling
        try:
            if isinstance(customer_id, str):
                hex_str = customer_id.strip().lower()
                if hex_str.startswith('0x'):
                    hex_str = hex_str[2:]
                if len(hex_str) % 2 != 0:
                    raise ValueError("customer_id hex must have even length")
                self._raw = bytes.fromhex(hex_str) if hex_str else b""
            elif isinstance(customer_id, (bytes, bytearray)):
                self._raw = bytes(customer_id)
            elif customer_id is None:
                self._raw = b""
            else:
                raise TypeError("customer_id must be hex str or bytes")
        except Exception:
            # Fallback to empty on invalid input
            self._raw = b""
        if len(self._raw) > 255:
            self._raw = self._raw[:255]

    def to_bytes(self):
        payload = struct.pack('>B', len(self._raw)) + self._raw
        header = struct.pack('>BBH', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self):
        return (
            f"CustomerId(type={self.sensor_type}, ver={self.sensor_version}, "
            f"len={len(self._raw)} bytes)"
        )
