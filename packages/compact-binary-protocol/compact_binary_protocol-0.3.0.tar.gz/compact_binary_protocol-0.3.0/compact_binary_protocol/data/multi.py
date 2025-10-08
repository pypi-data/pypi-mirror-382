import struct
from .constants import TYPE_MULTI

class DataMulti:
    def __init__(self, first_timestamp, interval, records):
        self.sensor_type = int(TYPE_MULTI)
        self.sensor_version = int(1)
        self.first_timestamp = first_timestamp
        self.interval = interval
        self.records = records

        if len(self.records) > 255:
            self.records = self.records[:255]

    def to_bytes(self):
        payload_header = struct.pack(
            '>IHB',
            int(self.first_timestamp),
            int(self.interval),
            len(self.records)
        )
        records_bytes = bytearray()
        for rec in self.records:
            temp = int(round(float(rec['temperature']) * 10))
            hum = int(round(float(rec['humidity']) * 10))
            records_bytes += struct.pack('>hh', temp, hum)
        payload = payload_header + bytes(records_bytes)
        header = struct.pack('>BBH', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self):
        rec_cnt = len(self.records) if self.records is not None else 0
        return (
            f"Multi(type={self.sensor_type}, ver={self.sensor_version}, "
            f"first_ts={self.first_timestamp}, "
            f"interval={self.interval}s, records={rec_cnt})"
        )
