"""Exceptions triggered to warn about internal errors related to data classes Factories classes."""


class AssonantDataHandlerFactoryError(Exception):
    """Custom Exception to warn when any error occurs inside AssonantDataHandlerFactory."""


class AssonantComponentFactoryError(Exception):
    """Custom Exception to warn when any error occurs inside AssonantComponentFactory."""


class AssonantEntryFactoryError(Exception):
    """Custom Exception to warn when any error occurs inside AssonantEntryFactory."""
