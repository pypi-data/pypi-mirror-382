"""Assonant Entry data class."""

from typing import Dict, Generator, Iterable, List, Optional, Type, Union

import numpy as np

from .assonant_data_class import AssonantDataClass
from .components import Beamline
from .data_handlers import DataField, DataHandler, TimeSeries
from .exceptions.data_classes_exceptions import (
    DataHandlerInsertionError,
    DataHandlerTakeageError,
    FieldCreationError,
    FieldInsertionError,
)


class Entry(AssonantDataClass):
    """Data classes that wraps data into a logical/temporal scope related to the experiment.

    Entries are used to group and represent data in a defined temporal/logical scope of the
    experimen. Every Entry instance must also have an Beamline object to identify with at
    least the beamline name it is related to.
    """

    beamline: Beamline
    name: str
    fields: Optional[Dict[str, DataHandler]] = {}

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
        from .factories import AssonantDataHandlerFactory

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
        from .factories import AssonantDataHandlerFactory

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
            name (str): name (str): Name attributed to passed DataHandler.
            new_data_handler (DataHandler): Any valid DataHandler object.

        Raises:
            DataHandlerInsertionError: Raised when the DataHandler type is not supported or an error occurs
            inside the specific method to add the DataHandlers to the component based in its type.
        """
        try:
            if isinstance(new_data_handler, DataField):
                self.add_field(name=name, new_field=new_data_handler)
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

    def take_data_handlers_from(self, entry: Union["Entry", List["Entry"]]):
        """Take DataHandlers from within an Entry or List of Entrys and add to itself.

        Taken DataHandlers are moved target Entries (passed entries) to
        take Entry (Entry which method was called from).

        Args:
            entry (Union[Entry, List[Entry]]): Entry or List of Entrys which DataHandlers will be taken.

        Raises:
            DataHandlerTakeageError: Raised when an error occurs when taking a DataHandler and trying to add to itself.
        """

        if not isinstance(entry, List):
            entry_list = [entry]
        else:
            entry_list = entry

        for target_entry in entry_list:

            target_entry_field_names = [*target_entry.fields.keys()]

            for field_name in target_entry_field_names:
                try:
                    field_data_handler = target_entry.fields.pop(field_name)
                    self.add_data_handler(name=field_name, new_data_handler=field_data_handler)
                except Exception as e:
                    raise DataHandlerTakeageError(f"Failed when trying to take '{field_name}' field from Entry") from e

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
