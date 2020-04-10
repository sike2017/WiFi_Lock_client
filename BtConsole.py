from prompt_toolkit import PromptSession
import view
import settings

import CustomException

class InputCommandRepeater:
    commandName = ""
    commandParameterList = []
    commandFunc = None

    def __init__(self, commandName, commandParameterList = [], commandFunc = None):
        self.commandName = commandName
        self.commandParameterList = commandParameterList
        self.commandFunc = commandFunc
    
    def generateCommandUsage(self) -> str:
        s = self.commandName
        s = s + " " + " ".join(self.commandParameterList)
        return s
    
    def execute(self, argumentList: list):
        return self.commandFunc(tuple(argumentList))

inputCommands = [
    InputCommandRepeater("unlock", ["user_id"]),
    InputCommandRepeater("lock", ["user_id"]),
    InputCommandRepeater("adduser", ["applicant_id"]),
    InputCommandRepeater("deluser", ["applicant_id", "target_id"]),
    InputCommandRepeater("reset", ["main_user_id"]),
    InputCommandRepeater("ping"),
    InputCommandRepeater("init", ["password"]),
    InputCommandRepeater("addguest", ["applicant_id", "endtimestamp32", "times16"]),
    InputCommandRepeater("gunlock", ["guest_key"]),
    InputCommandRepeater("glock", ["guest_key"]),
    InputCommandRepeater("connect", ["optional_device_address"]),
    InputCommandRepeater("disconnect"),
    InputCommandRepeater("help"),
    InputCommandRepeater("scan")
]
inputCommandList = [o.commandName for o in inputCommands]
inputCommandDict = {}
for inputCommandObject in inputCommands:
    inputCommandDict[inputCommandObject.commandName] = inputCommandObject

def help_local(argumentTuple) -> str:
    result = "Usage:\n"
    for item in inputCommandDict.values():
        result = "%s%s%s" %(result, " " * 4, item.generateCommandUsage())
        result = result + "\n"
    return result

inputCommandDict["unlock"].commandFunc = view.unlock_transmission
inputCommandDict["lock"].commandFunc = view.lock_transmission
inputCommandDict["adduser"].commandFunc = view.add_user_transmission
inputCommandDict["deluser"].commandFunc = view.del_user_transmission
inputCommandDict["reset"].commandFunc = view.reset_transmission
inputCommandDict["ping"].commandFunc = view.ping_transmission
inputCommandDict["init"].commandFunc = view.init_transmission
inputCommandDict["addguest"].commandFunc = view.add_guest_local
inputCommandDict["gunlock"].commandFunc = view.guest_unlock_transmission
inputCommandDict["glock"].commandFunc = view.guest_lock_transmission
inputCommandDict["connect"].commandFunc = view.connect_transmission
inputCommandDict["disconnect"].commandFunc = view.disconnect_trasmission
inputCommandDict["help"].commandFunc = help_local
inputCommandDict["scan"].commandFunc = view.scan

def commandExecute(text) -> bool:
    l = text.strip().split(" ")
    if len(l[0]) == 0:
        return False
    if l[0] not in inputCommandList:
        print("commant not exist")
        return False
    argumentList = l[1:]
    necessaryLength = 0
    for item in inputCommandDict[l[0]].commandParameterList:
        if item.startswith(settings.OPTIONAL_COMMAND_PREFIX):
            continue
        necessaryLength = necessaryLength + 1
    if len(argumentList) < necessaryLength:
        print("command format error")
        return False
    if l[0] in inputCommandList:
        result = 0
        try:
            result = inputCommandDict[l[0]].execute(l[1:])
            print(str(result))
            return True
        # except OSError as e:
        #     print(repr(e))
        #     return False
        except ValueError as e:
            print(repr(e))
            return False
        except CustomException.NotConnectException as e:
            print(repr(e))
            return False

def commandLoop():
    session = PromptSession()
    prompt = "> "
    while True:
        try:
            text = session.prompt(prompt)
            if not commandExecute(text):
                # command execute error
                continue
            if text.startswith("connect"):
                prompt = "% "
            elif text.startswith("disconnect"):
                prompt = "> "
        except KeyboardInterrupt:
            continue    # Control - C pressed. Try again.
        except EOFError:
            commandExecute("disconnect")
            break    # Control - D pressed.

if __name__ == "__main__":
    commandLoop()
