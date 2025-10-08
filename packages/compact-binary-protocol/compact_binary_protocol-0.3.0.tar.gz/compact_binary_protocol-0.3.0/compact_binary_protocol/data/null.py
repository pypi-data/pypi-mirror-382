import struct
from .constants import TYPE_NULL

class DataNull:
    def __init__(self):
        self.sensor_type = TYPE_NULL
        self.sensor_version = 0

    def to_bytes(self):
        # Empty payload
        payload = b''
        header = struct.pack('>BBH', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self):
        return f"Null(type={self.sensor_type}, ver={self.sensor_version})"
