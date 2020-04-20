import json
from custom_exception import InvalidId
from Cryptodome.Cipher import AES
from settings import BYTEORDER, DEFAULT_AES128_IV, NVS_KEY_MAX_SIZE, CIPHERED_BYTES_LENGTH_MAX_SIZE
from utillity import paddingBytes

import time

class User:
    def __init__(self, user_id: bytes, user_nvs_key = None, guest_id_list: [bytes] = []):
        self.user_id: bytes = user_id
        self.guest_id_list = guest_id_list
        if user_nvs_key is None:
            self.user_nvs_key = user_nvs_key
        elif isinstance(user_nvs_key, bytes):
            self.user_nvs_key: str = user_nvs_key[: user_nvs_key.find(0X00)].decode(encoding="ascii")
        elif isinstance(user_nvs_key, str):
            self.user_nvs_key = user_nvs_key

    def toJsonObject(self):
        return {
            "user_id": self.user_id.hex(),
            "user_nvs_key": str(self.user_nvs_key),
            "guest_id_list": [item.hex() for item in self.guest_id_list]
        }
    
    @classmethod
    def fromJsonObject(cls, d):
        return cls(bytes.fromhex(d["user_id"]), d["user_nvs_key"], d["guest_id_list"])
    
    def add(self):
        d = JsonStorage.load()
        if not "users" in d or not isinstance(d["users"], list):
            JsonStorage.initJsonFile()
        d["users"].append(self.toJsonObject())
        JsonStorage.dump(d)

    def delete(self):
        d = JsonStorage.load()
        if not "users" in d or not isinstance(d["users"], list):
            JsonStorage.initJsonFile()
        for item in d["users"]:
            if self.user_id.hex() == item["user_id"]:
                d["users"].remove(item)
                JsonStorage.dump(d)
                return
        raise InvalidId("invalid id")

    @classmethod
    def fromUserId(cls, userId: bytes):
        d = JsonStorage.load()
        userId = userId.hex()
        for item in d["users"]:
            if item["user_id"] == userId:
                return User.fromJsonObject(item)
        return None
    
    def addGuest(self, guest):
        d = JsonStorage.load()
        for item in d["users"]:
            if item["user_id"] == self.user_id.hex():
                item["guest_id_list"].append(guest.toJsonObject())
                JsonStorage.dump(d)
                return
        raise InvalidId("can not add a guest to an user which is not exist")
    
    def generateGuest(self, endTime: int):
        return Guest(self, endTime)

class Guest:
    @classmethod
    def encrypt(cls, user: User, endTime: int) -> (bytes, int):
        plainBytes = b""
        endTime = endTime.to_bytes(8, BYTEORDER)

        plainBytes += endTime
        plainBytes += user.user_id
        plainBytes = paddingBytes(plainBytes, 16)

        cipheredBytes = b""
        aes = AES.new(user.user_id, AES.MODE_CBC, DEFAULT_AES128_IV)
        cipheredBytes = aes.encrypt(plainBytes)

        finalBytes = b""
        user_nvs_key = user.user_nvs_key.encode(encoding="ascii") + int(0x00).to_bytes(1, BYTEORDER)
        finalBytes += paddingBytes(user_nvs_key, NVS_KEY_MAX_SIZE)
        cipheredBytesLength = len(cipheredBytes)
        finalBytes += cipheredBytesLength.to_bytes(CIPHERED_BYTES_LENGTH_MAX_SIZE, BYTEORDER)
        finalBytes += cipheredBytes
        return (finalBytes, cipheredBytesLength)

    def __init__(self, user: User, endTime: int):
        self.user: User = user
        self.endTime: int = endTime
        encryptResult = self.encrypt(user, endTime)
        self.encryptBytes: bytes = encryptResult[0]
        self.encryptBytesLength: int = encryptResult[1]
    
    def toJsonObject(self):
        return {
            "endTimestamp": str(self.endTime),
            "encryptBytes": self.encryptBytes.hex(),
            "encryptBytesLength": self.encryptBytesLength
        }

class JsonStorage:
    @staticmethod
    def initJsonFile():
        d = {
            "users":[]
        }
        f = open("./local_storage.json", "w", encoding="utf-8")
        json.dump(d, f, indent=4, ensure_ascii=False, separators=(",",":"))

    @staticmethod
    def load():
        f = open("./local_storage.json", encoding="utf-8")
        d = json.load(f)
        f.close()
        return d
    
    @staticmethod
    def dump(d):
        f = open("./local_storage.json", "w", encoding="utf-8")
        json.dump(d, f, indent=4, ensure_ascii=False, separators=(",", ":"))
        f.close()