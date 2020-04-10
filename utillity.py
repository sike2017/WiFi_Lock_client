from descriptor import ALL_RESPONSE_HEADERS, ALL_COMMANDS

def paddingBytes(s: bytes, n: int) -> bytes:
    bytesLength = len(s)
    if not bytesLength % n:
        return s
    result = s + bytes(n - bytesLength % n)

    return result

def getResponseHeaderNameByFlag(flag: int):
    # return None if not found
    headers = ALL_RESPONSE_HEADERS()
    names = headers.keys()
    for item in names:
        if headers.value(item) == flag:
            return item
    return None

def getRequestCommandNameByFlag(flag: int):
    # return None if not found
    commands = ALL_COMMANDS()
    names = commands.keys()
    for item in names:
        if commands.value(item) == flag:
            return item
    return None
