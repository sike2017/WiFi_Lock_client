from descriptor import ALL_COMMANDS, ALL_RESPONSE_HEADERS
from communicity import Request, Communicity, Package, Response
from settings import PACKAGE_SIZE, USER_ID_SIZE
from model import User, JsonStorage
from custom_exception import InvalidId

class ViewResult:
    pass

class ViewRemoteResult(ViewResult):
    def __init__(self, sendPak: Package, recvPak: Package):
        self.sendPak = sendPak
        self.recvPak = recvPak
        self.response = Response.fromPak(recvPak)
    
    def getSendPak(self):
        return self.sendPak
    
    def getRecvPak(self):
        return self.recvPak
    
    def getResponse(self):
        return self.response

class ViewLocalResult(ViewResult):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

commands = ALL_COMMANDS()
headers = ALL_RESPONSE_HEADERS()

def sendRequest(request: Request) -> ViewRemoteResult:
    # return (response, sendPackage, recvPackage)
    sendPackage = request.toPackage()
    recv = Communicity().send(sendPackage, PACKAGE_SIZE)
    recvPackage = Package.fromBytes(recv)
    result = ViewRemoteResult(sendPackage, recvPackage)
    if result.getResponse().flag != headers.RESPONSE_HEADER_PING and not result.getResponse().isOk():
        print("remote error")
    return result

def viewConnect(argList) -> ViewLocalResult:
    Communicity().connect()
    return ViewLocalResult("connected")

def viewDisconnect(argList) -> ViewLocalResult:
    Communicity().disconnect()
    return ViewLocalResult("disconnected")

def viewPing(argList) -> ViewRemoteResult:
    request = Request(commands.COMMAND_PING, b'')
    result = sendRequest(request)
    return result

def viewInit(argList) -> ViewRemoteResult:
    password = argList[0]
    request = Request.fromStr(commands.COMMAND_INIT, password)
    result = sendRequest(request)
    response = result.getResponse()
    if response.isOk():
        JsonStorage.initJsonFile()
        user = User(response.args[0:USER_ID_SIZE])
        user.add()
    return result

def viewAddUser(argList) -> ViewRemoteResult:
    requestId = bytes.fromhex(argList[0])
    request = Request(commands.COMMAND_ADD_USER, requestId)
    result = sendRequest(request)
    response = result.getResponse()
    if response.isOk():
        user = User(response.args[0:USER_ID_SIZE])
        user.add()
    return result

def viewDelUesr(argList) -> ViewRemoteResult:
    requestId = bytes.fromhex(argList[0])
    targetId = bytes.fromhex(argList[1])
    request = Request(commands.COMMAND_DEL_USER, requestId + targetId)
    result = sendRequest(request)
    response = result.getResponse()
    if response.isOk():
        user = User(targetId)
        try:
            user.delete()
        except InvalidId as e:
            print(e)
    return result

def viewOpenLock(argList) -> ViewRemoteResult:
    requestId = bytes.fromhex(argList[0])
    request = Request(commands.COMMAND_OPEN_LOCK, requestId)
    result = sendRequest(request)
    return result

def viewCloseLock(argList):
    requestId = bytes.fromhex(argList[0])
    request = Request(commands.COMMAND_CLOSE_LOCK, requestId)
    result = sendRequest(request)
    return result
