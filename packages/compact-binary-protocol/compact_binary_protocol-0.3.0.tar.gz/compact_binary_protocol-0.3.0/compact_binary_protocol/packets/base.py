import struct
import time

class Packet:
    def __init__(self, command, device_id, transaction_id=0, version=1, timestamp: int | None = None):
        # Ensure command is exactly 2 characters (pad or truncate)
        if len(command) == 1:
            self.command = command + '\0'
        elif len(command) >= 2:
            self.command = command[:2]
        else:
            self.command = '\0\0'
        self.device_id = device_id
        self.transaction_id = transaction_id
        self.version = version
        # Base timestamp (u32). Default to current time if not provided.
        self.timestamp = int(timestamp if timestamp is not None else int(time.time()))

    @staticmethod
    def _encode_imei_bcd(device_id_str: str) -> bytes:
        digits = ''.join(ch for ch in device_id_str if ch.isdigit())
        if len(digits) == 0:
            return b"\x00" * 8
        if len(digits) % 2 == 1:
            digits = '0' + digits
        b = bytearray()
        for i in range(0, len(digits), 2):
            low = int(digits[i+1])
            high = int(digits[i])
            b.append((high << 4) | low)
        return bytes(b)

    def build_header(self):
        device_id_bytes = Packet._encode_imei_bcd(self.device_id)
        header = struct.pack('>BBBHB',
                             self.version,
                             ord(self.command[0]),
                             ord(self.command[1]),
                             self.transaction_id,
                             len(device_id_bytes)) + device_id_bytes
        # Append base timestamp (u32)
        header += struct.pack('>I', self.timestamp)
        return header

    def to_bytes(self):
        raise NotImplementedError()

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Timestamp: {self.timestamp}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)
