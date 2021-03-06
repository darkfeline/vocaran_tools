#!/usr/bin/env python3

class ExitException(Exception):

    """Used to raise sys.exit()"""

    def __init__(self, code=0, *args):
        self.code = code
        super().__init__(*args)


class FileNotAvailableError(Exception):

    """Used when download file is not available"""


class DependencyError(Exception):

    """Used when dependency is not met"""


class DataException(Exception):

    """Base class for data-related exceptions"""


class FileFormatError(DataException):

    """Used when there's a problem with file formatting"""


class StructureError(DataException):

    """Used when there's a problem with data dir structure"""
