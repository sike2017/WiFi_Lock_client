OPTIONAL_COMMAND_PREFIX = "optional"
ADDRESS = "20:19:05:14:23:71"
IP = "192.168.4.1"
TCP_PORT =  2700

PACKAGE_SIZE = 64
RESERVED_BYTES_SIZE = 1
LOADING_SIZE = PACKAGE_SIZE - RESERVED_BYTES_SIZE
DEFAULT_AES128_IV = bytes(b"\x00"*16)
BYTEORDER = "little"
USER_ID_SIZE = 16