"""Assonant metadata retriever.

This submodule defines Metadata Retrievers objects to allow retrieving important
metadata for Assonant from different sources.
"""

from .assonant_metadata_retriever import AssonantMetadataRetriever
from .assonant_metadata_retriever_interface import IAssonantMetadataRetriever
from .exceptions import AssonantMetadataRetrieverError
from .metadata_retriever_factory import MetadataRetrieverFactoryError

__all__ = [
    "AssonantMetadataRetriever",
    "AssonantMetadataRetrieverError",
    "IAssonantMetadataRetriever",
    "MetadataRetrieverFactoryError",
]
