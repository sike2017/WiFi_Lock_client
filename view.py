from Transmission import Command
from Transmission import RespondHead
from Transmission import Respond
from Transmission import Request
import Transmission
import LocalStorage
import settings
from Cryptodome.Cipher import AES
import sys
import utillity

import bluetooth

jsonStorage = LocalStorage.JsonStorage()

def unlock_transmission(argumentTuple) -> Respond:
    request = Request(Command(Transmission.COMMAND_UNLOCK), argumentTuple[0])
    recBytes = request.send()
    return Respond.fromBytes(recBytes)

def lock_transmission(argumentTuple) -> Respond:
    request = Request(Command(Transmission.COMMAND_LOCK), argumentTuple[0])
    recBytes = request.send()
    return Respond.fromBytes(recBytes)

def init_transmission(argumentTuple) -> Respond:
    request = Request(Command(Transmission.COMMAND_INIT), argumentTuple[0].encode("ascii"))
    recBytes = request.send()
    respond = Respond.fromBytes(recBytes)
    if respond.head.isSuccess():
        jsonStorage._dumpDict(jsonStorage.jsonFileDict)
        LocalStorage.User.fromBytes(respond.additionalData, True).add()
    return respond

def add_user_transmission(argumentTuple) -> Respond:
    request = Request(Command(Transmission.COMMAND_ADD_USER), argumentTuple[0])
    recBytes = request.send()
    respond = Respond.fromBytes(recBytes)
    if respond.head.isSuccess():
        LocalStorage.User.fromBytes(respond.additionalData).add()
    return respond

def del_user_transmission(argumentTuple) -> Respond:
    request = Request(Command(Transmission.COMMAND_DELETE_USER), argumentTuple[0] + argumentTuple[1])
    recBytes = request.send()
    respond = Respond.fromBytes(recBytes)
    if respond.head.isSuccess():
        jsonStorage.deleteUserId(bytes.fromhex(argumentTuple[0]))
    return respond

def reset_transmission(argumentTuple) -> Respond:
    request = Request(Command(Transmission.COMMAND_RESET), argumentTuple[0])
    recBytes = request.send()
    respond = Respond.fromBytes(recBytes)
    if respond.head.isSuccess():
        jsonStorage._dumpDict(jsonStorage.jsonFileDict)
    return respond

def ping_transmission(argumentTuple) -> Respond:
    request = Request(Command(Transmission.COMMAND_PING), b"")
    recBytes = request.send()
    return Respond.fromBytes(recBytes)

def add_guest_local(argumentTuple) -> str:
    applicant_id = bytes.fromhex(argumentTuple[0])
    endtimestamp32 = int(argumentTuple[1], 10)
    times16 = int(argumentTuple[2], 10)

    key = applicant_id
    iv = settings.DEFAULT_AES128_IV
    enc = AES.new(key, AES.MODE_CBC, iv)
    user = jsonStorage.searchUser(applicant_id)
    if user is None:
        return "%s is not exist" %(applicant_id.hex())
    guest_id = user.newGuestId()
    guestOriginalBytes = applicant_id
    guestOriginalBytes = guestOriginalBytes + guest_id.to_bytes(1, settings.BYTEORDER)
    guestOriginalBytes = guestOriginalBytes + endtimestamp32.to_bytes(4, settings.BYTEORDER)
    guestOriginalBytes = guestOriginalBytes + times16.to_bytes(2, settings.BYTEORDER)
    guestOriginalBytes = utillity.paddingBytes(guestOriginalBytes, 16)
    encBytes = enc.encrypt(guestOriginalBytes)
    encBytes = bytes([user.user_index]) + encBytes
    jsonStorage.addGuest(
        applicant_id, LocalStorage.Guest(guest_id, endtimestamp32, times16, encBytes)
    )
    return encBytes.hex()

def guest_unlock_transmission(argumentTuple) -> Respond:
    request = Request(Command(Transmission.COMMAND_GUEST_UNLOCK), argumentTuple[0])
    recBytes = request.send()
    return Respond.fromBytes(recBytes)

def guest_lock_transmission(argumentTuple) -> Respond:
    request = Request(Command(Transmission.COMMAND_GUEST_LOCK), argumentTuple[0])
    recBytes = request.send()
    return Respond.fromBytes(recBytes)

def connect_transmission(argumentTuple) -> str:
    address = settings.ADDRESS
    if len(argumentTuple) > 0:
        address = argumentTuple[0]

    Transmission.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    # Transmission.sock.settimeout(settings.TIME_OUT)
    print("before connect")
    print("address: %s" %address)
    Transmission.sock.connect((address, settings.PORT))
    print("after connect")

    return "connected"

def disconnect_trasmission(argumentTuple) -> str:
    if Transmission.sock is not None:
        Transmission.sock.close()

    return "disconnected"

def scan(argumentTuple) -> str:
    s = ""
    dic = Transmission.getNearbyDevices()
    for item in dic.keys():
        s = s + "%s - %s\n" %(item, dic[item])
    return s
