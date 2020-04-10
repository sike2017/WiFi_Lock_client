import json
from custom_exception import InvalidId

class User:
    def __init__(self, user_id: bytes):
        self.user_id = user_id

    def toJsonObject(self):
        return {
            "user_id": self.user_id.hex()
        }
    
    @classmethod
    def fromJsonObject(cls, d):
        return cls(d["user_id"])
    
    def add(self):
        d = JsonStorage.load()
        if not "users" in d or not isinstance(d["users"], list):
            d["users"] = []
            print("model.py 21")
        d["users"].append(self.toJsonObject())
        JsonStorage.dump(d)

    def delete(self):
        d = JsonStorage.load()
        if not "users" in d or not isinstance(d["users"], list):
            d["users"] = []
        for item in d["users"]:
            if self.user_id.hex() == item["user_id"]:
                d["users"].remove(item)
                JsonStorage.dump(d)
                return
        raise InvalidId("invalid id")

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