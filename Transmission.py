import bluetooth
import abc
import settings
import CustomException
from SerialRFCOMM import SerialRFCOMM

sock = None

class BluetoothTransmission(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def toBytes(self):
        pass

    def send(self) -> bytes:
        if sock is None:
            raise CustomException.NotConnectException("Not connect.")
        return bluetoothSend(self.toBytes())

COMMAND_UNLOCK = 0X10
COMMAND_LOCK = 0X11
COMMAND_ADD_USER = 0x20
COMMAND_DELETE_USER = 0X21
COMMAND_RESET = 0x30
COMMAND_PING = 0x40
COMMAND_INIT = 0x50
COMMAND_GUEST_UNLOCK = 0x60
COMMAND_GUEST_LOCK = 0x61
COMMAND_INVALID = 0xFF    # invalid command will be turned into COMMAND_INVALID

commandList = [
    COMMAND_UNLOCK,
    COMMAND_LOCK,
    COMMAND_ADD_USER,
    COMMAND_DELETE_USER,
    COMMAND_RESET,
    COMMAND_PING,
    COMMAND_INIT,
    COMMAND_GUEST_UNLOCK,
    COMMAND_GUEST_LOCK,
    COMMAND_INVALID
]

class Command:
    command = None
    
    def __init__(self, data):
        # data can be int or an list-like object of int
        if type(data) is int:
            if data in commandList:
                self.command = data
            else:
                raise ValueError("invalid command: %02x" %data)
        else:
            if data[0] in commandList:
                self.command = data[0]
            else:
                raise ValueError("invalid command: %02x" %data)

    def toBytes(self) -> bytes:
        return bytes([self.command])
    
    def toInt(self) -> int:
        return self.command

RESPOND_HEAD_ERROR = 0x10
RESPOND_HEAD_SUCCESS = 0X11
RESPOND_HEAD_PING = 0x20
# if receieved the invalid command, respond with RESPOND_HEAD_INVALID
RESPOND_HEAD_INVALID = 0XFF

respondHeadList = [
    RESPOND_HEAD_ERROR,
    RESPOND_HEAD_SUCCESS,
    RESPOND_HEAD_PING,
    RESPOND_HEAD_INVALID
]

respondHeadDict = {
    RESPOND_HEAD_ERROR: "RESPOND_ERROR",
    RESPOND_HEAD_SUCCESS: "RESPOND_SUCCESS",
    RESPOND_HEAD_PING: "RESPOND_PING",
    RESPOND_HEAD_INVALID: "RESPOND_INVALID"
}

class RespondHead:
    head = None

    def __init__(self, data):
        # data can be int or an list-like object of int
        if type(data) == int:
            if data in respondHeadList:
                self.head = data
            else:
                raise ValueError("invalid RespondHead: %02x" %data)
        else:
            if data[0] in respondHeadList:
                self.head = data[0]
            else:
                raise ValueError("invalid RespondHead: %02x" %data)
    
    def toBytes(self) -> bytes:
        return bytes([self.head])
    
    def toInt(self) -> int:
        return self.head
    
    def __str__(self):
        return respondHeadDict[self.head]
    
    def isSuccess(self) -> bool:
        return self.head == RESPOND_HEAD_SUCCESS

class Respond:
    head = RespondHead(RESPOND_HEAD_INVALID)
    additionalData = bytes(settings.PACKAGE_SIZE - 1)

    def __init__(self, head: RespondHead, additionalData: bytes):
        self.head = head
        self.additionalData = additionalData
    
    def toBytes(self) -> bytes:
        return bytes(self.head.toBytes() + self.additionalData)
    
    @classmethod
    def fromBytes(cls, s):
        return cls(
            head = RespondHead(s[0]),
            additionalData = s[1:]
        )
    
    def __str__(self):
        return "%s: %s" %(str(self.head), self.additionalData.hex())

class Request(BluetoothTransmission):
    command = Command(COMMAND_INVALID)
    additionalData = bytes(settings.PACKAGE_SIZE - 1)

    def __init__(self, command: Command, additionalData: bytes):
        self.command = command
        if type(additionalData) == bytes:
            self.additionalData = additionalData
        elif type(additionalData) == bytearray:
            self.additionalData = bytes(additionalData)
        elif type(additionalData) == str:
            self.additionalData = bytes.fromhex(additionalData)
    
    def toBytes(self) -> bytes:
        return bytes(self.command.toBytes() + self.additionalData)


def getNearbyDevices() -> dict:
    dic = {}
    try:
        nearby_devices = bluetooth.discover_devices(lookup_names=True)
    except Exception as e:
        print(e)
        return {}
    for addr, name in nearby_devices:
        dic[addr] = name
    return dic

def devicesDictToStr(dictDevicesDic: dict) -> str:
    s = ""
    dic = dictDevicesDic
    for item in dic.keys():
        s = s + "%s - %s" %(item, dic[item])
    return s

def bluetoothSend(byteData: bytes) -> bytes:
    # send byte data by bluetooth and return receieved byte data
    print("send: %s" %byteData.hex())
    sock.send(byteData)
    print("sent")
    receievedData = b""
    print("receieved: ", end="")
    while True:
        tmpReceieved = sock.recv(settings.PACKAGE_SIZE)
        if tmpReceieved is None:
            break
        print("%s" %(tmpReceieved.hex()), end="")
        receievedData = receievedData + tmpReceieved
        if len(receievedData) >= settings.PACKAGE_SIZE:
            break
    print("")

    return receievedData
