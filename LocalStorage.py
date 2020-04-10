import json
import os
import sys
import settings
from Cryptodome.Cipher import AES

import utillity
    

class Guest:

    def __init__(
        self, 
        guest_id: int, endtimestamp32: int, times16: int, secret_key: bytes
    ):
        self.guest_id = guest_id
        self.endtimestamp32 = endtimestamp32
        self.times16 = times16
        self.secret_key = secret_key.hex()
    
    def keys(self):
        return ("guest_id", "endtimestamp32", "times16", "secret_key")
    
    def __getitem__(self, item):
        return getattr(self, item)
    
    def toJsonDict(self):
        return {
            "guest_id": self.guest_id,
            "endtimestamp32": self.endtimestamp32,
            "times16": self.times16,
            "secret_key": self.secret_key
        }
    
    @classmethod
    def fromDict(cls, d):
        return cls(
            d["guest_id"], d["endtimestamp32"], d["times16"], d["secret_key"]
        )

class User:
    def __init__(self, user_id: bytes, user_index: int, if_main: bool = False, guest_list = []):
        self.user_id: str = user_id.hex()
        self.user_index: int = user_index
        self.if_main: bool = if_main
        self.guest_list = guest_list

    def keys(self):
        return ("user_id", "user_index", "if_main", "guest_list")

    def __getitem__(self, item):
        return getattr(self, item)

    @classmethod
    def fromBytes(cls, s: bytes, if_main:bool = False):
        return cls(
            user_id = s[0:16],
            user_index = s[17],
            if_main = if_main,
            guest_list = []
        )

    @classmethod
    def fromDict(cls, d: dict):
        if isinstance(d["user_id"], str):
            d["user_id"] = bytes.fromhex(d["user_id"])
        if len(d["guest_list"]) > 0 and isinstance(d["guest_list"][0]["secret_key"], str):
            for item in d["guest_list"]:
                item["secret_key"] = bytes.fromhex(item["secret_key"])
        guest_list = [Guest.fromDict(g) for g in d["guest_list"]]
        return User(
            d["user_id"], d["user_index"], if_main=d["if_main"], 
            guest_list=guest_list
        )

    def addGuest(self, guest: Guest) -> None:
        self.guest_list.append(guest)
    
    def newGuestId(self) -> int:
        return len(self.guest_list)

    def toJsonDict(self) -> dict:
        return {
            "user_id": self.user_id,
            "user_index": self.user_index,
            "if_main": self.if_main,
            "guest_list": [item.toJsonDict() for item in self.guest_list]
        }

    def add(self):
        JsonStorage().addUser(self)

class JsonStorage(object):
    _instance = None

    def __init__(self):
        self.jsonFileName = "local_storage.json"
        self.jsonFileDict = {
            "users": []
        }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def _dumpDict(self, newDict):
        with open(self.jsonFileName, "w", encoding="utf-8") as f:
            json.dump(newDict, f, indent=4, separators=(",", ":"))

    def _loadJson(self):
        if not os.path.exists(self.jsonFileName):
            # file not exist
            open(self.jsonFileName, "w+").close()
            json.dump(self.jsonFileDict, open(self.jsonFileName, "w", encoding="utf-8"))
        d = None
        with open(self.jsonFileName, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d

    def addUserId(self, userId: bytes, userIndex: int) -> None:
        userDict = self._loadJson()
        userDict["users"].append(User(userId, userIndex))    # storage an user id as a hex string
        self._dumpDict(userDict)

    def deleteUserId(self, userId: bytes) -> bool:
        """
        Delete an user id from json file.
        If the user id is not exist return False, else return True.
        """
        userDict = self._loadJson()
        for user in userDict["users"]:
            if user["user_id"] == userId.hex():
                userDict["users"].remove(user)
                self._dumpDict(userDict)
                return True
        return False

    def getUserId(self, index: int) -> bytes:
        """
        Return an user id from json file.
        If the index is invalid raise IndexError.
        """
        userDict = self._loadJson()
        return bytes.fromhex(userDict["users"][index]["user_id"])
    
    def searchUser(self, userId: bytes) -> User:
        """
        Return an User object.
        If the user is not exist, return None.
        """
        userIdHex = userId.hex()
        userDict = self._loadJson()
        for item in userDict["users"]:
            if item["user_id"] == userIdHex:
                return User.fromDict(item)
        return None
    
    def addGuest(self, userId: bytes, guest: Guest):
        userDict = self._loadJson()
        for item in userDict["users"]:
            if item["user_id"] == userId.hex():
                item["guest_list"].append(dict(guest))
                self._dumpDict(userDict)
                return guest.guest_id
        return None

    def deleteGuest(self, userId: bytes, guest: Guest):
        userDict = self._loadJson()
        userIdHex = userId.hex()
        for item in userDict["users"]:
            if item["user_id"] == userIdHex:
                for g in item["guest_list"]:
                    if g["guest_id"] == guest.guest_id:
                        item["guest_list"].remove(g)
                        return g.guest_id
        return None
    
    def addUser(self, user: User):
        userDict = self._loadJson()
        userDict["users"].append(user.toJsonDict())
        self._dumpDict(userDict)
