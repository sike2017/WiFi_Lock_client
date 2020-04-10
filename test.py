import unittest
import BtConsole
import LocalStorage

class BtConsoleTest(unittest.TestCase):
    # test BtConsole.py
    DEFAULT_PASSWORD = "aabbccdd"
    localStorage = LocalStorage.JsonStorage()

    def _exc(self, command: str):
        print("COMMAND: %s" %command)
        result = BtConsole.commandExecute(command)
        self.assertEqual(result, True)

    def test_transmission(self):
        self._exc("connect")
        self._exc("ping")
        self._exc("init %s" %(self.DEFAULT_PASSWORD))
        mainUserId = self.localStorage.getUserId(0).hex()
        self._exc("lock %s" %(mainUserId))
        self._exc("unlock %s" %(mainUserId))
        self._exc("adduser %s" %(mainUserId))
        addedUserId = self.localStorage.getUserId(1).hex()
        self._exc("deluser %s %s" %(mainUserId, addedUserId))
        self._exc("reset %s" %(mainUserId))
        self._exc("disconnect")

if __name__ == "__main__":
    unittest.main()