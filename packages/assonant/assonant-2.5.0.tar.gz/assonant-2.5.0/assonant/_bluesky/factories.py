import json
from typing import Any, Dict, List, Union

from .data_parser import DocumentsDataParser
from .exceptions import BlueskyDataParserFactoryError


class DataParserFactory:
    """Bluesky DataParser Factory Class.

    The role of this class is to handle type checking and return the correct DataParser to deal
    with given Bluesky data source. It is also responsible to raise a exception if passed source
    is from a unsupported type.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating Assonant Component objects.
    """

    @staticmethod
    def create_data_parser(
        bluesky_data_source: Union[List[List[Union[str, Dict[str, Any]]]], str]
    ) -> DocumentsDataParser:
        """Instatiates a Suitable Bluesky DataParser to handle data parsing tasks over passed data source.

        Bluesky data must always be structure as the Bluesky Event-Model.
        Reference to it: https://github.com/bluesky/event-model

        Args:
            bluesky_data_source (Union[List[List[Union[str, Dict[str, Any]]]], str]): DataSource containing
            the bluesky data. Currently, supported formats are: JSON file containing bluesky events or a
            List of bluesky documents data presented also as  a list. The list with the document data has
            2 positions, the 1st is the bluesky identification for the document
            (start, event, stop, descriptor, ...) and the 2nd position the dict containing the document
            data.
        Raises:
            BlueskyDataParserError: Failed during DataParser creation or unsupported bluesky_data_source type.

        Returns:
            DataParser: Specific Bluesky DataParser able to handle tasks over passed bluesky_data_source.
        """
        if type(bluesky_data_source) is str:
            try:
                with open(bluesky_data_source, "r") as json_file:
                    bluesky_documents_list = json.load(json_file)
            except Exception as e:
                raise BlueskyDataParserFactoryError(
                    f"Failed to load bluesky documents data from JSON file with path: {bluesky_data_source}"
                ) from e
            return DocumentsDataParser(bluesky_documents_list=bluesky_documents_list)
        elif type(bluesky_data_source) is list:
            return DocumentsDataParser(bluesky_documents_list=bluesky_data_source)
        else:
            raise BlueskyDataParserFactoryError(
                f"Bluesky data source of type {type(bluesky_data_source)} not supported!"
            )
