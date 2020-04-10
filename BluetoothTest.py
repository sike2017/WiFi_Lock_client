import bluetooth
import SerialRFCOMM
import settings
import time

if __name__ == "__main__":
    # sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    # sock.connect(("98:D3:11:F8:1B:F4", 1))
    # s_rfcomm_r = SerialRFCOMM.SerialRFCOMM(
    #     "COM5", 
    #     settings.SERIAL_BAUDRATES, 
    #     settings.SERIAL_TIME_OUT
    # )
    # s_rfcomm_w = SerialRFCOMM.SerialRFCOMM(
    #     "COM5",
    #     settings.SERIAL_BAUDRATES,
    #     settings.SERIAL_TIME_OUT
    # )
    # while True:
    #     try:
    #         s_rfcomm_w.write(bytes.fromhex("10"))
    #         time.sleep(1)
    #         print(s_rfcomm_r.read(32).hex())
    #     except KeyboardInterrupt:
    #         exit(0)

    import bluetooth

    bd_addr = "98:D3:11:F8:1B:F4"

    port = 1

    sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    sock.connect((bd_addr, port))

    sock.send("hello!!")

    sock.close()




