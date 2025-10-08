# Central definitions of SensorData type codes
# Version numbers remain defined in each implementation class

TYPE_NULL = 0
TYPE_KV = 1
TYPE_LOCATION = 10
TYPE_CUSTOMER_ID = 11

TYPE_VERSIONS = 20
TYPE_NETWORK_INFO = 21
TYPE_DEVICE_STATUS = 22

TYPE_ENVIRONMENT = 100
TYPE_MULTI = 101
TYPE_STEPS = 102

__all__ = [
    'TYPE_NULL',
    'TYPE_ENVIRONMENT',
    'TYPE_MULTI',
    'TYPE_STEPS',
    'TYPE_VERSIONS',
    'TYPE_NETWORK_INFO',
    'TYPE_LOCATION',
    'TYPE_CUSTOMER_ID',
    'TYPE_KV',
]
