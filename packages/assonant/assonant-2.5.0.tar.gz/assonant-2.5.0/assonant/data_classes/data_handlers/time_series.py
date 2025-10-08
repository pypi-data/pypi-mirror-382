"""Assonant TimeSeries class."""

from typing import List, Type, Union

import numpy as np

from .data_field import DataField
from .data_handler import DataHandler


class TimeSeries(DataHandler):
    """Data class to handle any type of time series data."""

    value: DataField
    timestamps: DataField

    def set_value(self, value: Union[int, float, str, List, Type[np.ndarray], None]):
        """Set value to 'value' property from TimeSeries.

        Args:
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value to bet set to
            TimeSeries 'value' property.
        """
        self.value.set_value(value)

    def set_timestamps(self, value: Union[int, float, str, List, Type[np.ndarray], None]):
        """Set value to 'timestamps' property from TimeSeries.

        Args:
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value to bet set to
            TimeSeries 'timestamps' property.
        """
        self.timestamps.set_value(value)
