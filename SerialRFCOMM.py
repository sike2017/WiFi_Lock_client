import serial
import settings

class SerialRFCOMM:
    def __init__(self, port, baudrates, timeout):
        self.ser = serial.Serial(
            port, 
            baudrates, 
            timeout=timeout
        )

    def write(self, data: bytes):
        self.ser.write(data)

    def read(self, length=settings.PACKAGE_SIZE):
        return self.ser.read(length)

    def serialSend(self, data: bytes):
        self.write(data)
        return self.read()
