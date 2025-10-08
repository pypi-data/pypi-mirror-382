"""Assonant DataField class."""

from typing import Dict, List, Optional, Type, Union

import numpy as np

from ..exceptions import AssonantDataClassesError
from .data_handler import DataHandler


class DataField(DataHandler):
    """Data class to handle any type of base data, such as integers, floats, numpy arrays and lists."""

    value: Union[int, float, str, List, Type[np.ndarray], None]
    unit: Optional[str] = None
    extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {}

    def set_value(self, value: Union[int, float, str, List, Type[np.ndarray], None]):
        """Set value to 'value' property from DataField.

        Args:
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value to be set to
            DataField 'value' property.
        """
        self.value = value

    def set_unit(self, value: str):
        """Set value to 'unit' property from DataField.

        Args:
            value (str): Value to be set to DataField 'unit' property
        """
        self.unit = value

    def add_extra_metadata(self, metadata_name: str, value: Union[int, float, str, List, Type[np.ndarray], None]):
        """Add new metadata with passed name to extra_metadata dict from DataField.

        Args:
            metadata_name (str): Name of passed metadata to be created.
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value to be set to new extra_metadata.

        Raises:
            AssonantDataClassesError: Raised when a passed metadata name conflicts with an already existing key from
            'extra_metadata' dictionary from DataField.
        """

        if metadata_name not in self.extra_metadata.keys():
            self.extra_metadata[metadata_name] = value
        else:
            raise AssonantDataClassesError(
                f"'{metadata_name}' metadata already exists on DataFielf extra_metadata dict!"
            )

    def set_extra_metadata(self, metadata_name: str, value: Union[int, float, str, List, Type[np.ndarray], None]):
        """Set value to passed extra_metadata with passed name within DataField extra_metadata dict.

        Args:
            metadata_name (str): Name of existing metadata that value will be set.
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value to be set to existing extra_metadata.

        Raises:
            AssonantDataClassesError: Raised when a passed metadata name doesn't exists in 'extra_metadata'
            dictionary from DataField.
        """
        if metadata_name in self.extra_metadata.keys():
            self.extra_metadata[metadata_name] = value
        else:
            raise AssonantDataClassesError(f"'{metadata_name}' metadata don't exists on DataField extra_metadata dict!")
