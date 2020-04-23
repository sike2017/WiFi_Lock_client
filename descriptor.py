from settings import OPTIONAL_COMMAND_PREFIX

class ALL_ITEMS_BASE:
    def keys(self) -> [str]:
        return [item for item in self.__dict__]
    
    def value(self, name: str) -> str:
        # Return commands value. If the name is not exist, return None.
        if name in self.__dict__.keys():
            return self.__dict__[name]
        return None

class ALL_COMMANDS(ALL_ITEMS_BASE):
    # do not add any thing which is not a symbol of a command
    def __init__(self):
        self.COMMAND_DISCONNECT = 0x01
        self.COMMAND_OPEN_LOCK = 0x10
        self.COMMAND_CLOSE_LOCK = 0x11
        self.COMMAND_ADD_USER = 0x20
        self.COMMAND_DEL_USER = 0x21
        # self.COMMAND_RESET = 0x30
        self.COMMAND_PING = 0x40
        self.COMMAND_INIT = 0x50
        self.COMMAND_GUEST_OPEN_LOCK = 0x60
        self.COMMAND_GUEST_CLOSE_LOCK = 0x61
        self.COMMAND_SET_WIFI = 0x70
        self.COMMAND_VERSION = 0x80

class InstructionParam:
    def __init__(self, name, optional=False):
        self.name = name
        self.optional = optional

class InstructionModel:
    def __init__(self, name, paramList=[], text=""):
        self.name = name
        self.paramList = []
        if len(paramList) != 0:
            if isinstance(paramList[0], str):
                for s in paramList:
                    name = s
                    optional = False
                    prefix = OPTIONAL_COMMAND_PREFIX
                    if s.startswith(prefix):
                        optional = True
                    self.paramList.append(InstructionParam(name, optional))
        if len(self.paramList) == 0:
            self.paramList = paramList
        self.text = text

class ALL_INSTRUCTIONS(ALL_ITEMS_BASE):
    def __init__(self):
        self.connect = InstructionModel("connect", ["optional_ip"], "connect device")
        self.disconnect = InstructionModel("disconnect", text="disconnect with device")
        self.ping = InstructionModel("ping")
        self.init = InstructionModel("init", ["password"], "initlize device")
        self.openlock = InstructionModel("open", ["request_id"], "open the lock")
        self.closelock = InstructionModel("close", ["request_id"], "close the lock")
        self.adduser = InstructionModel("adduser", ["request_id"], "create a new user")
        self.deluser = InstructionModel("deluser", ["request_id", "target_id"], "delete a user")
        self.addguest = InstructionModel("addguest", ["request_id", "end_timestamp_in_format_str"], "add a guest")
        self.gopenlock = InstructionModel("gopenlock", ["cipher_data"], "guest open lock")
        self.gcloselock = InstructionModel("gcloselock", ["cipher_data"], "guest close lock")
        self.setwifi = InstructionModel("setwifi", ["request_id", "ssid", "optional_password"], "set wifi")
        self.ota = InstructionModel("ota", ["password", "image", "optional_local_port"], "ota update by wifi")
        self.remote_version = InstructionModel("remote_version", [], "get remote version")

        self.help = InstructionModel("help", [], "get help information")
    
    def getHelpInformation(self):
        content = ""
        for key in self.keys():
            value = self.value(key)
            paramNameList = []
            for param in value.paramList:
                if param.name.startswith(OPTIONAL_COMMAND_PREFIX):
                    paramNameList.append("[%s]" %param.name)
                else:
                    paramNameList.append(param.name)
            temp = "%s %s\n" %(value.name, " ".join(paramNameList))
            content = content + temp
        return content

class ALL_RESPONSE_HEADERS(ALL_ITEMS_BASE):
    def __init__(self):
        self.RESPONSE_HEADER_OK = 0x10
        self.RESPONSE_HEADER_FAIL = 0x11
        self.RESPONSE_HEADER_PING = 0x20
        # if receieved the invalid command, respond with RESPONSE_HEADER_INVALID
        self.RESPONSE_HEADER_INVALID = 0xFF
