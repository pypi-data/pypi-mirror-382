"""
compact_binary_protocol

A small, self-contained Python library that defines the compact binary protocol
used by Tartabit client components. It provides:
- Encoding helpers
- Data model classes for location and sensor data
- Packet classes for telemetry/configuration/power/motion events
- Decoding helpers for responses and header parsing

All multi-byte values are encoded using big-endian format.
"""

from .encodings import encode_var_string
from .decoders import PacketDecoder, DataReader
from .data import (
    DataLocation,
    DataEnvironment,
    DataMulti,
    DataNull,
    DataSteps,
    DataVersions,
    DataNetworkInfo,
    DataCustomerId,
    DataDeviceStatus,
    DataKv,
)
from .packets import Packet, TelemetryPacket, ConfigPacket

__all__ = [
    'encode_var_string',
    'PacketDecoder', 'DataReader',
    'DataLocation', 'DataEnvironment', 'DataMulti', 'DataNull', 'DataSteps', 'DataVersions', 'DataNetworkInfo', 'DataCustomerId', 'DataKv', 'DataDeviceStatus',
    'Packet', 'TelemetryPacket', 'ConfigPacket',
]
