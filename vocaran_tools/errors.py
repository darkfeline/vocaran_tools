#!/usr/bin/env python3

class ExitException(Exception):
    def __init__(self, code=0, *args):
        self.code = code
        super().__init__(*args)

    pass

class DataException(Exception):
    pass

class FileNotAvailableException(DataException):
    pass

class FileFormatError(DataException):
    pass

class StructureException(DataException):
    pass
