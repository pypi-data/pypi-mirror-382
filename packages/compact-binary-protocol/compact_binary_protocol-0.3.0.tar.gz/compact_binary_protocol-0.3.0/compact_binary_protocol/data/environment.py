import struct
from .constants import TYPE_ENVIRONMENT


class DataEnvironment:
    def __init__(self, temperature, humidity, illumination, motion):
        self.sensor_type = int(TYPE_ENVIRONMENT)
        self.sensor_version = 1
        self.temperature = float(temperature)
        self.humidity = float(humidity)
        self.illumination = float(illumination)
        self.motion = bool(motion)

    def to_bytes(self):
        payload = struct.pack('>HHHB', int(self.temperature * 10), int(self.humidity*10), int(self.illumination), self.motion)
        header = struct.pack('>BBH', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self):
        return f"Environment(type={self.sensor_type}, ver={self.sensor_version}, temp={self.temperature}°C, hum={self.humidity}%, illum={self.illumination}lx, motion={self.motion})"
