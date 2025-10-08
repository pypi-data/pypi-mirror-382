import struct
from .constants import TYPE_DEVICE_STATUS

class DataDeviceStatus:
    def __init__(self, battery: int, rssi: int):
        self.sensor_type = TYPE_DEVICE_STATUS
        self.sensor_version = 1
        self.battery = int(battery)
        self.rssi = int(rssi)

    def to_bytes(self):
        payload = struct.pack('>BB', self.battery, self.rssi)
        header = struct.pack('>BBH', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self):
        return (
            f"Steps(type={self.sensor_type}, ver={self.sensor_version}, "
            f"batt={self.battery}%, rssi={self.rssi})"
        )
