"""Exceptions triggered to warn about internal errors in Assonant File Writer module."""


class AssonantFileWriterError(Exception):
    """Assonant File Writer Error.

    Custom Exception to warn when any error occurs inside AssonantFileWriter
    """

    pass


class FileAlreadyExistsError(Exception):
    """File Writer Error.

    Custom Exception to warn when the file already exists when trying to write new data.
    """

    pass


class NeXusObjectAlreadyExistsError(Exception):
    """NeXus File Writer Error.

    Custom Exception to warn when trying to write an NeXus object that already exist in the NeXus file.

    """
