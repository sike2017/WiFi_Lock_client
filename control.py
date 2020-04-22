from descriptor import InstructionModel, InstructionParam, ALL_INSTRUCTIONS, ALL_RESPONSE_HEADERS
import view2
import communicity
from settings import PACKAGE_SIZE, BYTEORDER
from utillity import getRequestCommandNameByFlag, getResponseHeaderNameByFlag, printException
from socket import timeout
from custom_exception import InvalidId, CustomException

class Connecter:
    connectionTable = {}

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        instructions = ALL_INSTRUCTIONS()
        self.connect(instructions.connect, view2.viewConnect)
        self.connect(instructions.disconnect, view2.viewDisconnect)
        self.connect(instructions.ping, view2.viewPing)
        self.connect(instructions.init, view2.viewInit)
        self.connect(instructions.adduser, view2.viewAddUser)
        self.connect(instructions.deluser, view2.viewDelUesr)
        self.connect(instructions.openlock, view2.viewOpenLock)
        self.connect(instructions.closelock, view2.viewCloseLock)
        self.connect(instructions.addguest, view2.viewAddGuest)
        self.connect(instructions.gopenlock, view2.viewGuestOpenLock)
        self.connect(instructions.gcloselock, view2.viewGuestCloseLock)
        self.connect(instructions.setwifi, view2.viewSetWiFi)

    def connect(self, instructionModel, func):
        self.connectionTable[instructionModel.name] = func
    
    def func(self, instructionModel):
        return self.connectionTable[instructionModel.name]

class Runner:
    def __init__(self):
        self.connecter = Connecter()
        self.instructions = ALL_INSTRUCTIONS()
        self.headers = ALL_RESPONSE_HEADERS()
        self.comm = communicity.Communicity()
        self.recv = bytes()

    def run(self, text: str):
        text = text.strip()
        if text == "":
            return False
        textList = text.split(" ")
        value: InstructionModel = self.instructions.value(textList[0])
        if value is None:
            print("invalid command")
            return False
        if len(textList[1:]) < len([item for item in value.paramList if not item.optional]):
            print("arg format error")
            return False
        argList = textList[1:]
        try:
            viewResult = self.connecter.func(value)(argList)
        except ValueError as e:
            printException(e)
            return False
        except CustomException as e:
            printException(e)
            return False

        if isinstance(viewResult, view2.ViewRemoteResult) and not viewResult.isHttpConnection():
            package = viewResult.getSendPak()

            args = bytes()
            if len(package.loading) > 1:
                args = package.loading[1:]
            print("""
request
--------------------------------
reserved bytes: %s
request command: %s
request args: %s
--------------------------------
            """ %(package.reservedBytes,
            getRequestCommandNameByFlag(package.loading[0]),
            args))

            recvPak = viewResult.getRecvPak()
            headerName = getResponseHeaderNameByFlag(recvPak.loading[0])
            if headerName is None:
                headerName = recvPak.loading[0].to_bytes(1, BYTEORDER)
            if len(recvPak.loading) > 1:
                args = recvPak.loading[1:]
            print("""
response
--------------------------------
reserved bytes: %s
response header: %s
response args: %s
--------------------------------
            """ %(recvPak.reservedBytes,
            headerName,
            args))

        elif isinstance(viewResult, view2.ViewHttpResult):
            print(viewResult.getRaw())

        elif isinstance(viewResult, view2.ViewLocalResult):
            print(str(viewResult))

        return True
