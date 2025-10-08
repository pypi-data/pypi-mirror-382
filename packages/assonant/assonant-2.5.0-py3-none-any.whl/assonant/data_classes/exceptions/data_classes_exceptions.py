"""Exceptions triggered to warn about internal errors in data classes module."""


class AssonantDataClassesError(Exception):
    """Custom Exception to warn when any generic error occurs inside Assonant Data Classes Modules."""


class DataHandlerInsertionError(AssonantDataClassesError):
    """Custom Exception to warn when any error related to inserting data handler into Assonant Data Classes."""


class DataHandlerTakeageError(AssonantDataClassesError):
    """Custom Exception to warn when any error related to taking data handlers from another Assonant Data Classes."""


class FieldCreationError(AssonantDataClassesError):
    """Custom Exception to warn when any error related to creating fields for Assonant Data Classes."""


class FieldInsertionError(AssonantDataClassesError):
    """Custom Exception to warn when any error related to inserting fields into Assonant Data Classes."""


class AxisCreationError(AssonantDataClassesError):
    """Custom Exception to warn when any error related to creating positions for Assonant Data Classes."""


class AxisInsertionError(AssonantDataClassesError):
    """Custom Exception to warn when any error related to inserting positions into Assonant Data Classes."""


class SubcomponentInsertionError(AssonantDataClassesError):
    """Custom Exception to warn when any error related to inserting subcomponents into Assonant Data Classes."""
