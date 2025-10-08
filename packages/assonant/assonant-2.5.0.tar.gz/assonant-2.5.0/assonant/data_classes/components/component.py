"""Assonant Component abstract class."""

from typing import Dict, Generator, Iterable, List, Optional, Type, Union

import numpy as np

from ..assonant_data_class import AssonantDataClass
from ..data_handlers import Axis, DataField, DataHandler, TimeSeries
from ..enums import TransformationType
from ..exceptions.data_classes_exceptions import (
    AxisCreationError,
    AxisInsertionError,
    DataHandlerInsertionError,
    DataHandlerTakeageError,
    FieldCreationError,
    FieldInsertionError,
    SubcomponentInsertionError,
)


class Component(AssonantDataClass):
    """Abstract class that creates the base common requirements to define an Assonant Component.

    Components are more generic definitions which may be composed by many subcomponents if more
    detailing in its composition is desired.
    """

    name: str
    subcomponents: Optional[Dict[str, "Component"]] = {}
    positions: Optional[Dict[str, Axis]] = {}
    fields: Optional[Dict[str, DataHandler]] = {}

    def add_subcomponent(self, new_component: Union["Component", List["Component"]]):
        """Add new subcomponent or list of new subcomponents to component.

        Args:
            component (Union[Component, List[Component]]): Component object or List of Components which will be add as
            subcomponent from called Component object.

        Raises:
            SubcomponentInsertionError: Failure to insert Subcomponent to subcomponents dict from Component.
        """
        try:
            if isinstance(new_component, List):
                for _new_component in new_component:
                    if _new_component.name not in self.subcomponents:
                        self.subcomponents[_new_component.name] = _new_component
                    else:
                        # Generate a new name with a index to avoid equal names
                        new_name = self._generate_new_valid_name(
                            names_list=self.subcomponents, name=_new_component.name
                        )
                        _new_component.name = new_name
                        self.subcomponents[new_name] = _new_component
            elif isinstance(new_component, Component):
                if new_component.name not in self.subcomponents:
                    self.subcomponents[new_component.name] = new_component
                else:
                    # Generate a new name with a index to avoid equal names
                    new_name = self._generate_new_valid_name(names_list=self.subcomponents, name=new_component.name)
                    new_component.name = new_name
                    self.subcomponents[new_name] = new_component
            else:
                raise SubcomponentInsertionError(f"Invalid type for component being add! ({type(new_component)})")
        except Exception as e:
            raise SubcomponentInsertionError(
                f"Failed to add {new_component} Subcomponent to {self.name} subcomponents dict."
            ) from e

    def add_position(self, name: str, new_axis: Axis):
        """Add new positional field to component.

        Args:
            name (str): Axis name.
            axis (Axis): Axis DataHandler object.

        Raises:
            AxisInsertionError: Failure to insert Axis to Component positions dict.
        """
        try:
            if name not in self.positions:
                self.positions[name] = new_axis
            else:
                # Generate a new name with a index to avoid equal names
                new_name = self._generate_new_valid_name(names_list=self.positions, name=name)
                self.positions[new_name] = new_axis
        except Exception:
            raise AxisInsertionError(f"Failed to add {name} Axis to {self.name} Component.")

    def create_and_add_position(
        self,
        name: str,
        transformation_type: TransformationType,
        value: Union[int, float, str, List, Type[np.ndarray], None],
        unit: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
    ):
        """Create and add new positional field to component.

        Args:
            name (str): Axis name.
            transformation_type (TransformationType): Type of transformation done by axis.
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value related to axis
            collected data.
            unit (Optional[str], optional): Measurement unit related to value parameter.
            Defaults to None.
            extra_metadata (Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray],
            None]]], optional): Dictionary
            containing any aditional metadata related to collected data. Defaults to {}.

            Raises:
                AxisCreationError: Failure to create new Axis DataHandler with passed data.
                AxisInsertionError: Failure to insert new Axis DataHanlder into Component
                positions dict.
        """
        from ..factories import AssonantDataHandlerFactory

        try:
            new_axis = AssonantDataHandlerFactory.create_axis(
                transformation_type=transformation_type,
                value=value,
                unit=unit,
                extra_metadata=extra_metadata,
            )
        except Exception as e:
            raise AxisCreationError(f"Failed to create '{name}' Axis DataHandler for {self.name} Component.") from e
        try:
            self.add_position(name=name, new_axis=new_axis)
        except AxisInsertionError as e:
            raise e

    def create_and_add_timeseries_position(
        self,
        name: str,
        transformation_type: TransformationType,
        value: Union[int, float, str, List, Type[np.ndarray], None],
        timestamps: Union[int, float, str, List, Type[np.ndarray], None],
        unit: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
        timestamps_unit: Optional[str] = None,
        timestamp_extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
    ):
        """Create and Add new positional field to component.

        Args:
            name (str): Axis name
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
                AxisCreationError: Failure to create new Axis DataHandler with passed data.
                AxisInsertionError: Failure to insert new Axis DataHanlder into Component
                positions dict.
        """
        from ..factories import AssonantDataHandlerFactory

        try:
            new_axis = AssonantDataHandlerFactory.create_timeseries_axis(
                transformation_type=transformation_type,
                value=value,
                unit=unit,
                extra_metadata=extra_metadata,
                timestamps=timestamps,
                timestamps_unit=timestamps_unit,
                timestamp_extra_metadata=timestamp_extra_metadata,
            )
        except Exception as e:
            raise AxisCreationError(
                f"Failed to create '{name}' Axis Data TimeSeries with TimeSeries data for {self.name} Component."
            ) from e
        try:
            self.add_position(name=name, new_axis=new_axis)
        except AxisInsertionError as e:
            raise e

    def add_field(self, name: str, new_field: DataField):
        """Add new data field to component.

        Args:
            name (str): Field name
            data_field (DataField): DataField DataHandler object.

        Raises:
            FieldInsertionError: Failure on inserting DataField to Component fields dict.
        """
        try:
            if name not in self.fields:
                self.fields[name] = new_field
            else:
                # Generate a new name with a index to avoid equal names
                new_name = self._generate_new_valid_name(names_list=self.fields, name=name)
                self.fields[new_name] = new_field
        except Exception:
            raise FieldInsertionError(f"Failed to add '{name}' field to {self.name} Component.")

    def create_and_add_field(
        self,
        name: str,
        value: Union[int, float, str, List, Type[np.ndarray], None],
        unit: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
    ):
        """Create and add new data field.

        Args:
            name (str): Field name.
            value (Union[int, float, str, List, Type[np.ndarray], None]): Value related to field
            collected data.
            unit (Optional[str], optional): Measurement unit related to value parameter.
            Defaults to None.
            extra_metadata (Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]], optional): Dict
            containing any aditional metadata related to collected data. Defaults to {}.

        Raises:
            FieldCreationError: Failure on creating new DataField.
            FieldInsertionError: Failure on inserting DataField into Component fields dict.
        """
        from ..factories import AssonantDataHandlerFactory

        try:
            new_field = AssonantDataHandlerFactory.create_data_field(
                value=value,
                unit=unit,
                extra_metadata=extra_metadata,
            )
        except Exception as e:
            raise FieldCreationError(
                f"Failed to create '{name}' DataField Data Handler for {self.name} Component."
            ) from e
        try:
            self.add_field(name=name, new_field=new_field)
        except FieldInsertionError as e:
            raise e

    def add_timeseries_field(self, name: str, new_time_series_field: TimeSeries):
        """Add new data field to component that was collected as a TimeSeries.

        Args:
            name (str): Field name
            new_time_series_field (TimeSeries): TimeSeries DataHandler object.

        Raises:
            FieldInsertionError: Failure to insert TimeSeries to Component fields dict.
        """
        try:
            if name not in self.fields:
                self.fields[name] = new_time_series_field
            else:
                # Generate a new name with a index to avoid equal names
                new_name = self._generate_new_valid_name(names_list=self.fields, name=name)
                self.fields[new_name] = new_time_series_field
        except Exception:
            raise FieldInsertionError(f"Failed to add '{name}' TimeSeries field to {self.name} Component.")

    def create_and_add_timeseries_field(
        self,
        name: str,
        value: Union[int, float, str, List, Type[np.ndarray], None],
        timestamps: Union[int, float, str, List, Type[np.ndarray], None],
        unit: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
        timestamps_unit: Optional[str] = None,
        timestamp_extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray], None]]] = {},
    ):
        """Create and add new data field to component that data was collected as a TimeSeries.

        Args:
            name (str): Field name.
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
                FieldCreationError: Failure on creating new DataField.
                FieldInsertionError: Failure on inserting DataField into Component fields dict.
        """
        from ..factories import AssonantDataHandlerFactory

        try:
            new_field = AssonantDataHandlerFactory.create_timeseries_field(
                value=value,
                unit=unit,
                extra_metadata=extra_metadata,
                timestamps=timestamps,
                timestamps_unit=timestamps_unit,
                timestamp_extra_metadata=timestamp_extra_metadata,
            )
        except Exception as e:
            raise FieldCreationError(
                f"Failed to create '{name}' TimeSeries Data Handler for {self.name} Component."
            ) from e
        try:
            self.add_timeseries_field(name=name, new_time_series_field=new_field)
        except FieldInsertionError as e:
            raise e

    def add_data_handler(self, name: str, new_data_handler: DataHandler):
        """Add new DataHandler to its specific dictionary within Component class.

        This method is a generic way to add any type of DataHandler to a component. It just
        call the specific underlying method to add that type of DataHandler to the Component.

        Args:
            name (str): Name attributed to passed DataHandler.
            new_data_handler (DataHandler): Any valid DataHandler object.

        Raises:
            DataHandlerInsertionError: Raised when the DataHandler type is not supported or an error occurs
            inside the specific method to add the DataHandlers to the component based in its type.
        """
        try:
            if isinstance(new_data_handler, DataField):
                self.add_field(name=name, new_field=new_data_handler)
            elif isinstance(new_data_handler, Axis):
                self.add_position(name=name, new_axis=new_data_handler)
            elif isinstance(new_data_handler, TimeSeries):
                self.add_timeseries_field(name=name, new_time_series_field=new_data_handler)
            else:
                raise DataHandlerInsertionError(
                    f"Adding DataHandler of type: {type(new_data_handler)} is not supported yet."
                )
        except Exception as e:
            raise DataHandlerInsertionError(
                f"Failed to add DataHandler of type {type(new_data_handler)} to {self.name} Component."
            ) from e

    def take_data_handlers_from(self, component: Union["Component", List["Component"]]):
        """Take DataHandlers from within a Component or list of Components and add to itself.

        PS: Taken DataHandlers are moved from target Components (passed component) to
        taker Component (Component which method was called from).

        Args:
            component (Union[Component, List[Component]]): Component or List of Components which DataHandlers
            will be taken.

        Raises:
            DataHandlerTakeageError: Raised when an error occurs when taking a DataHandler and trying to add
            to itself.
        """

        if not isinstance(component, List):
            components_list = [component]
        else:
            components_list = component

        for target_component in components_list:

            target_component_field_names = [*target_component.fields.keys()]
            target_component_position_names = [*target_component.positions.keys()]

            for field_name in target_component_field_names:
                try:
                    field_data_handler = target_component.fields.pop(field_name)
                    self.add_data_handler(name=field_name, new_data_handler=field_data_handler)
                except Exception as e:
                    raise DataHandlerTakeageError(
                        f"Failed when trying to take '{field_name}' DataHandler from '{target_component.name}' Component to add to '{self.name}' Component"
                    ) from e

            for position_name in target_component_position_names:
                try:
                    position_data_handler = target_component.positions.pop(position_name)
                    self.add_data_handler(name=position_name, new_data_handler=position_data_handler)
                except Exception as e:
                    raise DataHandlerTakeageError(
                        f"Failed when trying to take '{position_name}' DataHandler from '{target_component.name}' Component to add to '{self.name}' Component"
                    ) from e

    def _generate_new_valid_name(self, names_list: Iterable, name: str) -> str:
        """Generate a new name that don't exist on passed names list.

        Args:
            names_list (_type_): Iterable containing already existing names.
            name (str): Current name that will be changed to fit passed list.

        Returns:
            str: New unique name based on the passed name that don't exist on passed names list.
        """
        # Generate a new name with a index to avoid equal names
        new_name_generator = self._indexed_name_generator(name)
        new_name = next(new_name_generator)
        while new_name in names_list:
            new_name = next(new_name_generator)
        return new_name

    def _indexed_name_generator(self, name: str) -> Generator[str, None, None]:
        """Generator for creating indexed names.

        Args:
            name (str): Reference name to be indexed by generator.

        Yields:
            Generator[str, None, None]: New indexed name based on passed name.
        """
        i = 1
        while True:
            new_name = f"{name} ({i})"
            yield new_name
            i += 1
