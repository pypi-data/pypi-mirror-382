from abc import ABC
from typing import Callable, Dict, List

from ._nexus_file_writer import NexusFileWriter
from .assonant_file_writer_interface import IAssonantFileWriter
from .exceptions import FileWriterFactoryError


class FileWriterFactory(ABC):
    """Abstract Factory for creating Assonant File Writers.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating Assonant Component objects.

    Uses a registry-based approach so that new file formats can be added
    without modifying the core creation logic (Open/Closed principle).

    Example:
        FileWriterFactory.register_file_format("myformat", MyFileWriter)
        writer = FileWriterFactory.create_file_writer("myformat")
    """

    _creators: Dict[str, Callable[[], IAssonantFileWriter]] = {}

    @staticmethod
    def register_file_format(file_format: str, creator: Callable[[], IAssonantFileWriter]) -> None:
        """Register a file format with its creator callable.

        Args:
            file_format (str): File format key (lowercase recommended).
            creator (Callable[[], IAssonantFileWriter]): Function or class returning a
            IAssonantFileWriter instance.
        """
        if not callable(creator):
            raise FileWriterFactoryError("Creator must be callable and return an IAssonantFileWriter instance.")

        FileWriterFactory._creators[file_format] = creator

    @staticmethod
    def create_file_writer(file_format: str) -> IAssonantFileWriter:
        """Create a file writer instance for the given format.

        Args:
            file_format (str): Target file format.

        Raises:
            FileWriterFactoryError: If the format is unsupported.

        Returns:
            IAssonantFileWriter: File writer instance.
        """
        try:
            creator = FileWriterFactory._creators[file_format]
        except KeyError:
            raise FileWriterFactoryError(
                f"'{file_format}' file format isn't currently supported. "
                f"Supported formats: {list(FileWriterFactory._creators.keys())}"
            )

        return creator()

    @staticmethod
    def get_supported_file_formats() -> List[str]:
        """Return a list of supported file formats."""
        return list(FileWriterFactory._creators.keys())


# === Register built-in formats here ===
FileWriterFactory.register_file_format("nexus", NexusFileWriter)
