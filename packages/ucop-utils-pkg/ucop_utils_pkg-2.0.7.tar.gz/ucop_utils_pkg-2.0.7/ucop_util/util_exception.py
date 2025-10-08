"""
Custom exceptions raised by various ucop-util-pkg modules.
"""

__all__ = [
    'ValueNotFoundError',
    'NameLenghtError',
    'NameError',
    'EmptyFileError',
    'EmptyDataFrameError',
]


class Error(Exception):
    """Base class for exceptions in this ucop-util-pkg package."""
    pass


class ValueNotFoundError(Error):
    """Exception raised when a matching value is not found in the stack.
    Attributes
    ----------
    message: str
            Explanation of the error.
    """
    def __init__(self, message, value):
        self.message = message
        self.value = value


class NameLenghtError(Error):
    """Exception raised when file name length is invalid.
    Attributes
    ----------
    message: str
            Explanation of the error.
    file_name: str
            Name of the invalid file.
    length: integer
            Length of the file name.
    """
    def __init__(self, message, file_name, length):
        self.message = message
        self.file_name = file_name
        self.length = length


class NameError(Error):
    """Exception raised for file naming standard violations.
    Attributes
    ----------
    message: str
            Explanation of the error.
    file_name: str
            Name of the invalid file.
    """
    def __init__(self, message, file_name):
        self.message = message
        self.file_name = file_name


class EmptyFileError(Error):
    """Exception raised for empty(zero-length) file.
    Attributes
    ----------
    message: str
            Explanation of the error.
    file_name: str
            Name of the empty file.
    """
    def __init__(self, message, file_name):
        self.message = message
        self.file_name = file_name


class EmptyDataFrameError(Error):
    """Exception raised when Spark SQL returns zero rows.
    Attributes
    ----------
    message: str
            Explanation of the error.
    """
    def __init__(self, message):
        self.message = message
