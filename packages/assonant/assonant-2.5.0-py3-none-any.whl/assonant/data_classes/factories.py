"""Factories used to abstract and centralize Assonant data classes instanciation process."""

import importlib
from typing import Dict, List, Optional, Type, Union

import numpy as np

from assonant.naming_standards import BeamlineName

from .components import Beamline, Component
from .data_handlers import Axis, DataField, TimeSeries
from .entry import Entry
from .enums import TransformationType
from .exceptions import (
    AssonantComponentFactoryError,
    AssonantDataHandlerFactoryError,
    AssonantEntryFactoryError,
)


class AssonantComponentFactory:
    """Assonant Component Factory Class.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating Assonant Component objects.
    """

    @staticmethod
    def create_component_by_class_name(class_name: str, component_name: str) -> Component:
        """Create an Assonant data class Component based on the class name passed in a string.

        Args:
            class_name (str): String with value equal to the name of a AssonantDataClass type.
            component_name (str): Name given to the component that will be created.

        Raises:
            AssonantComponentFactoryException: Passed 'class_name' argument is invalid.

        Returns:
            Component: Named Component object of type equals to the 'class_name' parameter.
        """
        try:
            component_class = getattr(importlib.import_module("assonant.data_classes.components"), class_name)
            component = component_class(name=component_name)
        except Exception as e:
            raise AssonantComponentFactoryError(
                f"An Error ocurred when creating Assonant Component by the following class name: {class_name}"
            ) from e
        return component

    @staticmethod
    def create_component_by_class_type(class_type: Component, component_name: str) -> Component:
        """Create an Assonant data class Component based on the class type passed.

        Args:
            class_type (Component): Assonant Component type of the class that will be created.
            component_name (str): Name given to the component that will be created.

        Raises:
            AssonantComponentFactoryException: Passed 'class_type' argument is invalid.

        Returns:
            Component: Named Component object of 'class_type' type.
        """
        try:
            component = class_type(name=component_name)
        except Exception as e:
            raise AssonantComponentFactoryError(
                f"An Error ocurred when creating Assonant Component by the following class type: {class_type}"
            ) from e
        return component


class AssonantDataHandlerFactory:
    """NeXus Data Handler Factory Class.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating Assonant Data Handler objects.
    """

    @staticmethod
    def create_data_handler(
        value: Union[int, float, str, List, Type[np.ndarray], None],
        unit: Optional[str] = None,
        transformation_type: Optional[TransformationType] = None,
        extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
        timestamps: Union[int, float, str, List, Type[np.ndarray], None] = None,
        timestamps_unit: Optional[str] = None,
        timestamp_extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
    ) -> Union[DataField, Axis, TimeSeries]:
        """Create the best fitting DataHandler object based on passed data.

        Args:
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value related to collected data.
            unit (Optional[str], optional): Measurement unit related to value parameter. Defaults to None.
            extra_metadata (Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]], optional): Dict
            containing any aditional metadata related to collected data. Defaults to {}.
            transformation_type (Optional[TransformationType], optional): TransformationType related to Axis data.
            Defaults to None.
            timestamps (Union[int, float, str, List, Type[np.ndarray], None], optional): Timestamps related to
            collected data. Defaults to None.
            timestamps_unit (Optional[str], optional): Measurement unit related to timestamps parameter.
            Defaults to None.
            timestamp_extra_metadata (Dict[str, Union[int, float, str, List, Type[np.ndarray], None]], optional):
            Dictionary containing extra metadata about timestamps field. Defaults to {}.

        Returns:
            Union[DataField, Axis, TimeSeries]: DataHandler object depeding on passed parameters:
            1) If timestamps != None AND transformationType != None method returns a TimeSeries with 'value'
            being an Axis.
            2) If timestamps != None AND transformationType == None method returns a  TimeSeries with 'value'
            being a DataField.
            3) If timestamps == None AND transformationType != None method returns an Axis.
            4) If timestamps == None AND transformationType == None method returns a DataField.

        """
        # Check key optional fields that changes the used DataHandler class
        if timestamps is None and timestamps_unit is None and timestamp_extra_metadata == {}:
            # It is not a TimeSeries monitored ...
            if transformation_type is not None:
                # Axis
                new_data_handler = AssonantDataHandlerFactory.create_axis(
                    transformation_type=transformation_type, value=value, unit=unit, extra_metadata=extra_metadata
                )
            else:
                # DataField
                new_data_handler = AssonantDataHandlerFactory.create_data_field(
                    value=value, unit=unit, extra_metadata=extra_metadata
                )
        else:
            # It is a TimeSeries monitored ...
            if transformation_type is not None:
                # Axis
                new_data_handler = AssonantDataHandlerFactory.create_timeseries_axis(
                    transformation_type=transformation_type,
                    value=value,
                    timestamps=timestamps,
                    unit=unit,
                    extra_metadata=extra_metadata,
                    timestamps_unit=timestamps_unit,
                    timestamp_extra_metadata=timestamp_extra_metadata,
                )
            else:
                # DataField
                new_data_handler = AssonantDataHandlerFactory.create_timeseries_field(
                    value=value,
                    timestamps=timestamps,
                    unit=unit,
                    extra_metadata=extra_metadata,
                    timestamps_unit=timestamps_unit,
                    timestamp_extra_metadata=timestamp_extra_metadata,
                )

        return new_data_handler

    @staticmethod
    def create_data_field(
        value: Union[int, float, str, List, Type[np.ndarray], None],
        unit: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
    ) -> DataField:
        """Create new DataField handler.

        Args:
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value related to field
            collected data.
            unit (Optional[str], optional): Measurement unit related to value parameter.
            Defaults to None.
            extra_metadata (Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]], optional): Dict
            containing any aditional metadata related to collected data. Defaults to {}.

        Raises:
            AssonantDataHandlerFactoryException: Failure during objects creation.

        Returns:
            DataField: New DataField object handlind given values.
        """
        try:
            new_field = DataField(
                value=value,
                unit=unit,
                extra_metadata=extra_metadata,
            )
        except Exception as e:
            raise AssonantDataHandlerFactoryError("Failed to create new DataField handler.") from e

        return new_field

    @staticmethod
    def create_axis(
        transformation_type: TransformationType,
        value: Union[int, float, str, List, Type[np.ndarray], None],
        unit: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
    ) -> Axis:
        """Create new Axis handler.

        Args:
            transformation_type (TransformationType): Type of transformation done by axis.
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value related to axis
            collected data.
            unit (Optional[str], optional): Measurement unit related to value parameter.
            Defaults to None.
            extra_metadata (Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray],
            None]]], optional): Dictionary
            containing any aditional metadata related to collected data. Defaults to {}.

        Raises:
            AssonantDataHandlerFactory: Failure during objects creation.

        Returns:
            Axis: New Axis object handling given data.
        """
        try:
            new_axis = Axis(
                transformation_type=transformation_type,
                value=AssonantDataHandlerFactory.create_data_field(
                    value=value,
                    unit=unit,
                    extra_metadata=extra_metadata,
                ),
            )
        except Exception as e:
            raise AssonantDataHandlerFactoryError("Failed to create new Axis handler") from e

        return new_axis

    @staticmethod
    def create_timeseries_field(
        value: Union[int, float, str, List, Type[np.ndarray], None],
        timestamps: Union[int, float, str, List, Type[np.ndarray], None],
        unit: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
        timestamps_unit: Optional[str] = None,
        timestamp_extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
    ) -> TimeSeries:
        """Create new Timeseries handler to handle timestamped DataField data.

        Args:
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value related to field
            collected data.
            timestamps (Union[int, float, str, List, Type[np.ndarray], None]): Timestamps related to data collected
            from the field.
            unit (Optional[str], optional): Measurement unit related to value parameter.
            Defaults to None.
            extra_metadata (Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray],
            None]]], optional): Dictionary
            containing any aditional metadata related to collected data. Defaults to {}.
            timestamps_unit (Optional[str], optional): Measurement unit related to
            timestamp field. Defaults to None.
            timestamp_extra_metadata (Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray],
            None]]], optional): Dictionary
            containing extra metadata about timestamps field. Defaults to {}.

        Raises:
            AssonantDataHandlerFactoryException: Failure during objects creation.

        Returns:
            TimeSeries: New TimeSeries object handling given timestamped data.
        """
        try:
            new_field = TimeSeries(
                value=AssonantDataHandlerFactory.create_data_field(
                    value=value,
                    unit=unit,
                    extra_metadata=extra_metadata,
                ),
                timestamps=AssonantDataHandlerFactory.create_data_field(
                    value=timestamps,
                    unit=timestamps_unit,
                    extra_metadata=timestamp_extra_metadata,
                ),
            )
        except Exception as e:
            raise AssonantDataHandlerFactoryError("Failed to create new TimeSeries handler.") from e

        return new_field

    @staticmethod
    def create_timeseries_axis(
        transformation_type: TransformationType,
        value: Union[int, float, str, List, Type[np.ndarray], None],
        timestamps: Union[int, float, str, List, Type[np.ndarray], None],
        unit: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
        timestamps_unit: Optional[str] = None,
        timestamp_extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
    ) -> Axis:
        """Create new TimeSeries handler to handle timestamped Axis data.

        Args:
            transformation_type (TransformationType): Transformation type of the Axis
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value related to
            axis collected data
            timestamps (Union[int, float, str, List, Type[np.ndarray], None]): Timestamps
            related to data collected from the axis.
            unit (Optional[str], optional): Measurement unit related to value
            field. Defaults to None.
            extra_metadata (Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray],
            None]]], optional): Dictionary
            containing extra metadata about value field. Defaults to {}.
            tracked it as a TimeSeries. Defaults to None.
            timestamps_unit (Optional[str], optional): Measurement unit related to
            timestamp field. Defaults to None.
            timestamp_extra_metadata (Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray],
            None]]], optional): Dict
            containing extra metadata about timestamps field. Defaults to {}.

        Raises:
            AssonantDataHandlerFactoryException: ailure during objects creation.

        Returns:
            Axis: New Axis object handling given timestamped data.
        """
        try:
            new_axis = Axis(
                transformation_type=transformation_type,
                value=AssonantDataHandlerFactory.create_timeseries_field(
                    value=value,
                    unit=unit,
                    extra_metadata=extra_metadata,
                    timestamps=timestamps,
                    timestamps_unit=timestamps_unit,
                    timestamp_extra_metadata=timestamp_extra_metadata,
                ),
            )
        except Exception as e:
            raise AssonantDataHandlerFactoryError("Failed to create Axis DataHandler with TimeSeries data.") from e

        return new_axis


class AssonantEntryFactory:
    """Assonant Entry Factory Class.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating Assonant Entry objects.
    """

    @staticmethod
    def create_entry(entry_name: str, beamline_name: BeamlineName):
        """Create Assonant Entry from a given Beamline.

        Args:
            acquisition_moment (AcquisitionMoment): Enum that defines Acquisition Moment related to entry.
            beamline_name (BeamlineName): BeamlineName enum that defines which Beamline the entry is related to.

        Returns:
            Entry: Assonant Entry for the respective BeamlineName.
        """
        try:
            beamline = AssonantComponentFactory.create_component_by_class_type(Beamline, beamline_name.value)
            beamline.create_and_add_field(name="name", value=beamline_name.value)
            entry = Entry(name=entry_name, beamline=beamline)
        except Exception as e:
            raise AssonantEntryFactoryError(
                f"An Error ocurred when creating an Entry for Beamline '{beamline_name}'."
            ) from e
        return entry
