class CustomException(Exception):
    def __init__(self, msg):
        self.msg = msg
    
    def __repr__(self):
        return self.msg
    
    def __str__(self):
        return self.__repr__()

class PackageSizeOverflow(CustomException):
    pass

class Unconnect(CustomException):
    pass

class InvalidId(CustomException):
    pass

class CustomValueError(CustomException):
    pass

class CustomFileNotExist(CustomException):
    pass
