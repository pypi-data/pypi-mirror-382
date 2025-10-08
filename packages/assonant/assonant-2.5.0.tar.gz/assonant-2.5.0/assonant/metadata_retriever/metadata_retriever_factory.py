from abc import ABC
from pathlib import Path
from typing import Callable, Dict, List

from ._csv_metadata_retriever import CSVMetadataRetriever
from .assonant_metadata_retriever_interface import IAssonantMetadataRetriever
from .enums import MetadataSourceFileFormat
from .exceptions import MetadataRetrieverFactoryError


def get_file_format(data_source_file_path: str) -> str:
    """Extract file extension from the given path.

    Args:
        data_source_file_path (str): Path to data source file.

    Raises:
        FileNotFoundError: If the path is invalid or not a file.

    Returns:
        str: File extension without '.' character.
    """
    path = Path(data_source_file_path)
    if not path.is_file():
        raise FileNotFoundError(f"'{data_source_file_path}' is not a valid file!")
    return path.suffix[1:]


class MetadataRetrieverFactory(ABC):
    """Abstract Factory for creating Assonant Metadata Retrievers.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating Assonant Metadata Retrievers.

    Uses a registry-based approach so that new metadata retrievers can be added
    without modifying the core creation logic (Open/Closed principle).

    Example:
        MetadataRetrieverFactory.register_file_format("csv", CSVMetadataRetriever)
        retriever = MetadataRetrieverFactory.create_metadata_retriever("data.csv")
    """

    _creators: Dict[str, Callable[[str], IAssonantMetadataRetriever]] = {}

    @staticmethod
    def register_file_format(file_format: str, creator: Callable[[str], IAssonantMetadataRetriever]) -> None:
        """Register a file format with its creator callable.

        Args:
            file_format (str): File format key (lowercase recommended).
            creator (Callable[[str], IAssonantMetadataRetriever]): Function or class
                returning an IAssonantMetadataRetriever instance.

        Raises:
            MetadataRetrieverFactoryError: If passed creator is not a callable object.

        """
        if not callable(creator):
            raise MetadataRetrieverFactoryError(
                "Creator must be callable and return an IAssonantMetadataRetriever instance."
            )

        MetadataRetrieverFactory._creators[file_format] = creator

    @staticmethod
    def create_metadata_retriever(metadata_source_file_path: str) -> IAssonantMetadataRetriever:
        """Create a metadata retriever instance for the given file.

        Args:
            metadata_source_file_path (str): Path to metadata source file.

        Raises:
            MetadataRetrieverFactoryError: If the file format is unsupported or invalid.

        Returns:
            IAssonantMetadataRetriever: Metadata retriever instance.
        """
        try:
            file_format = get_file_format(metadata_source_file_path)
        except Exception:
            raise MetadataRetrieverFactoryError(f"'{metadata_source_file_path}' is not a file!")

        try:
            creator = MetadataRetrieverFactory._creators[file_format]
        except KeyError:
            raise MetadataRetrieverFactoryError(
                f"'{file_format}' file format isn't currently supported. "
                f"Supported formats: {list(MetadataRetrieverFactory._creators.keys())}"
            )

        return creator(metadata_source_file_path)

    @staticmethod
    def get_supported_file_formats() -> List[str]:
        """Return a list of supported file formats."""
        return list(MetadataRetrieverFactory._creators.keys())


# === Register built-in formats here ===
MetadataRetrieverFactory.register_file_format(MetadataSourceFileFormat.CSV.value, CSVMetadataRetriever)
