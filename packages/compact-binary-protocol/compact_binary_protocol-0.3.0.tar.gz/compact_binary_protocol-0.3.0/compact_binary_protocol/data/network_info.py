import struct
from ..encodings import encode_var_string
from .constants import TYPE_NETWORK_INFO

class DataNetworkInfo:
    def __init__(self, mcc: str, mnc: str, rat: str):
        # Assign a distinct sensor type id
        self.sensor_type = TYPE_NETWORK_INFO
        self.sensor_version = 1
        self.mcc = '' if mcc is None else str(mcc)
        self.mnc = '' if mnc is None else str(mnc)
        self.rat = '' if rat is None else str(rat)

    def to_bytes(self):
        payload = encode_var_string(self.mcc) + encode_var_string(self.mnc) + encode_var_string(self.rat)
        header = struct.pack('>BBH', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self):
        return (
            f"NetworkInfo(type={self.sensor_type}, ver={self.sensor_version}, "
            f"mcc='{self.mcc}', mnc='{self.mnc}', rat='{self.rat}')"
        )
