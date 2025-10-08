import struct
from ..encodings import encode_var_string
from .constants import TYPE_VERSIONS

class DataVersions:
    def __init__(self, software_version: str, modem_version: str):
        self.sensor_type = TYPE_VERSIONS
        self.sensor_version = 1
        self.software_version = str(software_version) if software_version is not None else ''
        self.modem_version = str(modem_version) if modem_version is not None else ''

    def to_bytes(self):
        payload = encode_var_string(self.software_version) + encode_var_string(self.modem_version)
        header = struct.pack('>BBH', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self):
        return (
            f"Versions(type={self.sensor_type}, ver={self.sensor_version}, "
            f"software='{self.software_version}', modem='{self.modem_version}')"
        )