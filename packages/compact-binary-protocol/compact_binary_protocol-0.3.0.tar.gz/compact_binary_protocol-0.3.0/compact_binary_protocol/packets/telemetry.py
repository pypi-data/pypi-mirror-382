import struct
from .base import Packet

class TelemetryPacket(Packet):
    """
    Telemetry packet with an event field to cover periodic telemetry and motion events.
    Body (v2):
      - event (u8)
      - data_count (u8)
      - data items...
    Note: Timestamp has moved to the base packet header (u32)
    """
    def __init__(self, imei, timestamp, transaction_id, event, data=None):
        """
        Compat constructor:
        - New style: TelemetryPacket(imei, timestamp, txn_id, data, event=0)
        - Legacy style: TelemetryPacket(imei, timestamp, txn_id, command, data)
          where command is one of 'T', 'M+', 'M-'. Event will be mapped accordingly.
        """
        super().__init__(event, imei, transaction_id, 1, timestamp=timestamp)
        # normalize data to a list
        if data is None:
            self.data = []
        elif isinstance(data, (list, tuple)):
            self.data = list(data)
        else:
            self.data = [data]

    def to_bytes(self):
        header = self.build_header()
        data_count_val = len(self.data)
        body = struct.pack('>B', data_count_val)
        body += b''.join(sd.to_bytes() for sd in self.data)
        return header + body

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        descs = []
        for sd in self.data:
            try:
                descs.append(sd.describe())
            except Exception:
                descs.append(str(sd))
        data_str = '[' + ', '.join(descs) + ']'
        print(f"  data count: {len(self.data)}")
        print(f"  datas: {data_str}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)
