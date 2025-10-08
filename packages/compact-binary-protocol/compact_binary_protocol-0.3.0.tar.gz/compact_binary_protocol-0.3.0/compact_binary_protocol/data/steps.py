import struct
from .constants import TYPE_STEPS

class DataSteps:
    def __init__(self, steps: int):
        self.sensor_type = TYPE_STEPS
        self.sensor_version = 1
        self.steps = int(steps)

    def to_bytes(self):
        payload = struct.pack('>i', self.steps)
        header = struct.pack('>BBH', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self):
        return (
            f"Steps(type={self.sensor_type}, ver={self.sensor_version}, "
            f"steps={self.steps})"
        )
