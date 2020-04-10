def paddingBytes(s: bytes, n: int) -> bytes:
    bytesLength = len(s)
    if not bytesLength % n:
        return s
    result = s + bytes(n - bytesLength % n)

    return result