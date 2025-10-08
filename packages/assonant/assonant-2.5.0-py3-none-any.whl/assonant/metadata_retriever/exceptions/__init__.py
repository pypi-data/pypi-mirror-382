"""Assonant metadata retriever exceptions.

This submodule defines Exceptions used all over the metadata retriever module and its submodules.
"""

from .factories_exceptions import MetadataRetrieverFactoryError
from .metadata_retrievers_exceptions import AssonantMetadataRetrieverError

__all__ = ["AssonantMetadataRetrieverError", "MetadataRetrieverFactoryError"]
