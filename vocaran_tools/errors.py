#!/usr/bin/env python3

class QuitException(Exception):
    pass

class FileNotAvailableException(Exception):
    pass

class DataException(Exception):
    pass

class FileFormatError(DataException):
    pass

class DMException(DataException):
    pass

class InitException(DMException):
    pass

class DataException(DMException):
    pass
