"""Assonant Axis data handler."""

from typing import List, Type, Union

import numpy as np

from ..enums import TransformationType
from .data_field import DataField
from .data_handler import DataHandler
from .time_series import TimeSeries


class Axis(DataHandler):
    """Data class to handle data related to an axis position.

    When axis position is static the 'value' field must contain a single value and when it varies over time, it
    should be an array or TimeSeries.
    """

    transformation_type: TransformationType
    value: Union[DataField, TimeSeries]

    def set_value(self, value: Union[int, float, str, List, Type[np.ndarray], None]):
        """Set value to 'value' property from Axis.

        Args:
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value to bet set to
            Axis 'value' property.
        """
        self.value.set_value(value)

    def set_transformation_type(self, value: TransformationType):
        """Set value to 'transformation_type' property from Axis.

        Args:
            value (TransformationType): Enum of value respective to Axis transformation type.
        """
        self.transformation_type = value
