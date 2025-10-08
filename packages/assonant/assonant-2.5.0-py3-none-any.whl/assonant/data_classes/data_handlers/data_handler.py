"""Assonant DataHandler abstract class."""

from typing import Any

from ..assonant_data_class import AssonantDataClass


# TODO: Make this class abstract
class DataHandler(AssonantDataClass):
    """Abstract class that creates the base common requirements to define an Assonant DataHandler."""

    value: Any

    def set_value(self, value: Any):
        """Set value to DataHandler 'value' property.

        This MUST be overrided by child classes when specific logic based on the
        DataHandler type need to be performed.

        Args:
            value (Any): Value to be set to the 'value' property from the DataHandler
        """
        self.value = value
