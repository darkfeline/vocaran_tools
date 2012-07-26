#!/usr/bin/env python3

class QuitException(Exception):
    pass

class FileNotAvailableException(Exception):
    pass

# DMExceptions

class DMException(Exception):
    pass

class InitException(DMException):
    pass

class DataException(DMException):
    pass
