from abc import ABC
from pathlib import Path
from typing import Any, Callable, Dict, List

from ._bluesky_data_retriever import BlueskyDataRetriever
from .assonant_data_retriever_interface import IAssonantDataRetriever
from .enums import DataSourceFileFormat
from .exceptions import AssonantDataRetrieverError


def get_file_format(data_source_file_path: str) -> str:
    """Extract file extension from the given path.

    Args:
        data_source_file_path (str): Path to data source file.

    Raises:
        AssonantDataRetrieverError: If the path is invalid or not a file.

    Returns:
        str: File extension without '.' character.
    """
    path = Path(data_source_file_path)
    if not path.is_file():
        raise AssonantDataRetrieverError(f"'{data_source_file_path}' is not a valid file!")
    return path.suffix[1:]


class DataRetrieverFactory(ABC):
    """Abstract Factory for creating Assonant Data Retrievers.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating Assonant Metadata Retrievers.

    Uses a registry-based approach so that new data retrievers can be added
    without modifying the core creation logic (Open/Closed principle).

    Example:
        DataRetrieverFactory.register_file_format("json", BlueskyDataRetriever)
        retriever = DataRetrieverFactory.create_data_retriever("data.json")
    """

    _creators: Dict[str, Callable[[Any], IAssonantDataRetriever]] = {}

    @staticmethod
    def register_file_format(file_format: str, creator: Callable[[Any], IAssonantDataRetriever]) -> None:
        """Register a file format with its creator callable.

        Args:
            file_format (str): File format key (lowercase recommended).
            creator (Callable[[Any], IAssonantDataRetriever]): Function or class
                returning an IAssonantDataRetriever instance.

        Raises:
            AssonantDataRetrieverError: If passed creator is not callable.
        """
        if not callable(creator):
            raise AssonantDataRetrieverError("Creator must be callable and return an IAssonantDataRetriever instance.")

        DataRetrieverFactory._creators[file_format] = creator

    @staticmethod
    def create_data_retriever(data_source: Any) -> IAssonantDataRetriever:
        """Create a data retriever instance for the given data source.

        Args:
            data_source (Any): Data source to retrieve data from.
                - str: File path (extension determines retriever type).
                - list: Already loaded Bluesky documents.

        Raises:
            AssonantDataRetrieverError: If the file format or data source type is unsupported.

        Returns:
            IAssonantDataRetriever: Data retriever instance.
        """
        if isinstance(data_source, str):
            # File path case
            try:
                file_format = get_file_format(data_source)
            except Exception:
                raise AssonantDataRetrieverError(f"'{data_source}' is not a valid file!")

            try:
                creator = DataRetrieverFactory._creators[file_format]
            except KeyError:
                raise AssonantDataRetrieverError(
                    f"'{file_format}' file format isn't currently supported. "
                    f"Supported formats: {list(DataRetrieverFactory._creators.keys())}"
                )

            return creator(data_source)

        elif isinstance(data_source, list):
            # In-memory Bluesky data
            try:
                creator = DataRetrieverFactory._creators[DataSourceFileFormat.JSON.value]
            except KeyError:
                raise AssonantDataRetrieverError(
                    f"Bluesky in-memory data requires JSON retriever, "
                    f"but it is not registered! Supported formats: "
                    f"{list(DataRetrieverFactory._creators.keys())}"
                )
            return creator(data_source)

        else:
            raise AssonantDataRetrieverError("Data source type not supported for data retrieving!")

    @staticmethod
    def get_supported_file_formats() -> List[str]:
        """Return a list of supported file formats."""
        return list(DataRetrieverFactory._creators.keys())


# === Register built-in retrievers here ===
DataRetrieverFactory.register_file_format(DataSourceFileFormat.JSON.value, BlueskyDataRetriever)
