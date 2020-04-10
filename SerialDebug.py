import serial
from settings import SERIAL_PORT, BAUDRATES, SERIAL_TIME_OUT, PACKAGE_SIZE
from time import sleep

def serialSend(byteData: bytes) -> bytes:
    com = serial.Serial(SERIAL_PORT, BAUDRATES, timeout=SERIAL_TIME_OUT)
    print("send: %s" %byteData.hex())
    com.write(byteData)
    print("sent")
    recData = com.read()
    print("receieved: %s" %(recData.hex()))
    com.close()
    
    return recData
