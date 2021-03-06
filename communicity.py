from settings import PACKAGE_SIZE, BYTEORDER, RESERVED_BYTES_SIZE
from custom_exception import PackageSizeOverflow, Unconnect
from utillity import getResponseHeaderNameByFlag
import socket
from descriptor import ALL_RESPONSE_HEADERS, ALL_COMMANDS

class Package:

    def __init__(self):
        self.reservedBytes = None
        self.data = None
        self.loading = None
        self.length = None
    
    @classmethod
    def fromLoading(cls, loading: bytes):
        # build a Package from loading
        # this function will full the reserved bytes
        # the reserved bytes will be b'\00'
        r = Package()
        r.reservedBytes = b"\00"
        r.loading = loading
        r.data = r.reservedBytes + loading
        return r
    
    @classmethod
    def fromBytes(cls, data: bytes):
        # build a Package from bytes
        # the reserved bytes will be read from data[0] and write into the Package
        r = Package()
        r.reservedBytes = data[0].to_bytes(1, BYTEORDER)
        r.loading = data[1:]
        r.data = r.reservedBytes + data
        return r

    def toBytes(self):
        if len(self.data) > PACKAGE_SIZE:
            raise PackageSizeOverflow("package size must be little or equal with %d" %PACKAGE_SIZE)
        return self.data
    
    def getLoading(self):
        return self.loading

class Communicity:

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = object.__new__(cls)
        return cls._instance

    # def __init__(self):
    #     self.socket = None

    def connect(self, ip, port) -> None:
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.settimeout(10)
        self.socket.connect((ip, port))
        print(self.socket)

    def send(self, data: Package, length) -> bytes:
        if not hasattr(self, "socket"):
            raise Unconnect("must connect to a device before send")
        self.socket.sendall(data.toBytes(), PACKAGE_SIZE)
        recv = self.socket.recv(PACKAGE_SIZE)
        return recv

    def disconnect(self) -> None:
        if hasattr(self, "socket"):
            self.socket.close()
    
    def getpeername(self) -> (str, int):
        # get remote (ip, port)
        return self.socket.getpeername()

    def getsockname(self) -> (str, int):
        # get local (ip, port)
        return self.socket.getsockname()

    def isConnected(self) -> bool:
        r = self.send(Package.fromLoading(ALL_COMMANDS().COMMAND_PING), PACKAGE_SIZE)
        if len(Package.fromBytes(r).loading) != 0:
            return True
        return False

class Loading:
    def __init__(self, flag: int, b: bytes):
        self.flag = flag
        self.args = b
        self.data = self.flag.to_bytes(1, BYTEORDER) + self.args

    def toBytes(self):
        return self.data
    
    @classmethod
    def fromStr(cls, flag: bytes, s: str):
        r = cls(flag, s.encode(encoding="utf-8"))
        return r
    
    @classmethod
    def fromPak(cls, pack: Package):
        r = cls(pack.loading[0], pack.loading[1:])
        return r

    def toPackage(self):
        return Package.fromLoading(self.toBytes())

    def __str__(self):
        return self.data.hex()

class Response(Loading):
    def __str__(self):
        name = getResponseHeaderNameByFlag(self.flag)
        if not name is None:
            return "%s: %s" %(name, self.args.hex())
        else:
            return self.data.hex()
    
    def isOk(self) -> bool:
        if self.flag == ALL_RESPONSE_HEADERS().RESPONSE_HEADER_OK:
            return True
        return False

class Request(Loading):
    pass
