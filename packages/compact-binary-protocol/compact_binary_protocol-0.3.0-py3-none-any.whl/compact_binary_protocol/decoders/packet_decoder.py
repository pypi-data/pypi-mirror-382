class PacketDecoder:
    """Utility class for decoding compact-binary packets."""

    @staticmethod
    def parse_response_data(data_str):
        """
        Parse the response data string and extract the 4th parameter.
        Example input: "1,4,0,\"01410001\",\"52.59.84.1\",10104"
        Returns the 4th parameter (e.g., "01410001") or None if not found.
        """
        try:
            parts = []
            current_part = ""
            in_quotes = False
            for char in data_str:
                if char == '"':
                    in_quotes = not in_quotes
                    current_part += char
                elif char == ',' and not in_quotes:
                    parts.append(current_part)
                    current_part = ""
                else:
                    current_part += char
            if current_part:
                parts.append(current_part)
            if len(parts) >= 4:
                fourth_param = parts[3].strip('"')
                return fourth_param
            return None
        except Exception:
            return None

    @staticmethod
    def decode_packet_header(hex_str):
        """
        Decode the packet header from a hex string.
        Header format: <ver><cmd1><cmd2><txnId><imeiLen><imeiBCD...><timestamp u32>
        Returns tuple: (version, command, transaction_id, timestamp, remainder_bytes) or (None, None, None) on error.
        """
        try:
            data = bytes.fromhex(hex_str)
            if len(data) < 5:
                return (None, None, None)
            version = data[0]
            cmd1 = chr(data[1]) if len(data) > 1 else '\0'
            cmd2 = chr(data[2]) if len(data) > 2 else '\0'
            command = cmd1 + cmd2
            txn_id = int.from_bytes(data[3:5], byteorder='big')
            data = data[5:]
            return (version, command, txn_id, data)
        except Exception:
            return (None, None, None)
