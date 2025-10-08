"""Tests focused on validating Assonant Components/Entry methods that add information to it"""

import pytest

from assonant.data_classes.data_handlers import Axis, DataField, TimeSeries
from assonant.data_classes.enums import TransformationType
from assonant.data_classes.factories import AssonantDataHandlerFactory

from ..utils import (
    assert_axis_content,
    assert_axis_equality,
    assert_component_equality,
    assert_data_field_content,
    assert_data_fields_equality,
    assert_timeseries_content,
    assert_timeseries_equality,
    get_fixture_values,
)
from .test_data_handler_factory import create_test_params_combinations


@pytest.mark.parametrize("method", ["specific", "generic"])
@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(DataField))
def test_add_field(value, unit, metadata, method, example_base_component, request):
    """
    Validate that add_field and add_data_handler methods from Components correctly
    add DataField object to its internal fields dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must add DataField within its fields dictionary
        - Added DataField must be identified with the same name it was given during add_field method
        - DataField object within Component fields dictionary must be equivalent to how it was before insertion
    """

    # To avoid creating lots of different fixtures, manually create DataField DataHandler using Factory
    # if this test passes, other tests related to adding DataField, don't need to deal with all data types.
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)

    data_field = AssonantDataHandlerFactory.create_data_field(
        value=input_value,
        unit=input_unit,
        extra_metadata=input_metadata,
    )
    data_field_name = "data_field"

    if method == "specific":
        target_method_ref = example_base_component.add_field
    if method == "generic":
        target_method_ref = example_base_component.add_data_handler

    target_method_ref(data_field_name, data_field.model_copy(deep=True))

    # Assert DataField was add to fields dict
    assert len(example_base_component.fields.items()) == 1

    # Assert correct name was given to DataField within fields dict and that it remained unchanged.
    assert_data_fields_equality(example_base_component.fields[data_field_name], data_field)


@pytest.mark.parametrize("method", ["specific", "generic"])
def test_add_field_with_name_conflict(
    example_base_component, example_int_1d_array_data_field, example_float_2d_array_data_field, method
):
    """
    Validate that add_field and add_data_handler method from Components correctly add
    DataField object to its internal fields dictionary and handles name conflicts.

    Expected Behavior:
        - Both added DataFields must be within Component fields internal dict
        - The first added DataField must not suffer any change from how it was before
        - Any subsequent DataField added that has the same name with another already existing from the fields
        dict from Component must have its name automatically updated to a new unique name by adding an index in
        front the original passed name (e.g: <field_name> (1))
    """
    field_name = "field_name"

    if method == "specific":
        target_method_ref = example_base_component.add_field
    elif method == "generic":
        target_method_ref = example_base_component.add_data_handler

    target_method_ref(field_name, example_int_1d_array_data_field.model_copy(deep=True))
    target_method_ref(field_name, example_float_2d_array_data_field.model_copy(deep=True))

    # Assert both DataField objects were add to positions dict
    assert len(example_base_component.fields.items()) == 2

    # 1st DataField name and content must be unchanged
    assert_data_fields_equality(example_base_component.fields[field_name], example_int_1d_array_data_field)

    # 2nd DataField name must be the same as the 1st with a index due to name conflict and its content must be unchanged
    assert_data_fields_equality(example_base_component.fields[field_name + " (1)"], example_float_2d_array_data_field)


@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(DataField))
def test_add_field_methods_consistency(value, unit, metadata, example_base_component, request):
    """Validate that both add_field and add_data_handler methods from Components result in
    the same outcome when adding DataField to Component.

    Expected Behavior:
        - Both added DataField must be within its respective fields internal dict
        - Both added DataField must be indentified with the same name within its respective fields internal dict
        - Both added DataField must be equivalent
    """

    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)

    data_field = AssonantDataHandlerFactory.create_data_field(
        value=input_value,
        unit=input_unit,
        extra_metadata=input_metadata,
    )
    data_field_name = "data_field"

    component_1 = example_base_component.model_copy(deep=True)
    component_2 = example_base_component

    component_1.add_field(data_field_name, data_field)
    component_2.add_data_handler(data_field_name, data_field)

    assert_data_fields_equality(component_1.fields[data_field_name], component_2.fields[data_field_name])


@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(DataField))
def test_create_and_add_field(value, unit, metadata, example_base_component, request):
    """
    Validate that create_and_add_field method from Components correctly
    create and add DataField object to its internal fields dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must create a new DataField with passed data
        - Base Component must add the new created DataField within its fields dictionary
        - Added DataField must be identified with the same name it was given during create_and_add_field method
        - DataField object created by the Component must preserve passed data values.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)

    data_field_name = "data_field"
    example_base_component.create_and_add_field(data_field_name, input_value, input_unit, input_metadata)

    # Assert created DataField was add to fields dict
    assert len(example_base_component.fields.items()) == 1

    # Assert correct name was given to DataField within fields dict and that it remained unchanged
    assert_data_field_content(example_base_component.fields[data_field_name], input_value, input_unit, input_metadata)


def test_create_and_add_field_with_name_conflict(
    example_float_1d_array, example_int_1d_array, example_unit, example_metadata, example_base_component
):
    """
    Validate that create_and_add_field method from Components correctly
    create and add DataField object to its internal fields dictionary and handles name conflict.

    Expected Behavior:
        - Both DataFields must be created
        - Both created DataFields must be add to Component fields dictionary
        - The first create and added DataField must have its name and content preserved
        - The second create and added DataField must have its content preserved but name updated
        to a new unique name by adding an index in front of the original anem (e.g: <data_field_name> (1))
    """
    data_field_name = "data_field"
    example_base_component.create_and_add_field(data_field_name, example_float_1d_array, example_unit, example_metadata)
    example_base_component.create_and_add_field(data_field_name, example_int_1d_array, example_unit, example_metadata)

    # Assert both created DataFields were add to fields dict
    assert len(example_base_component.fields.items()) == 2

    # 1st DataField name and content must be unchanged
    assert_data_field_content(
        example_base_component.fields[data_field_name], example_float_1d_array, example_unit, example_metadata
    )

    # 2nd DataField name must be the same as the 1st with an index due to name conflict and
    # its content must be unchanged
    assert_data_field_content(
        example_base_component.fields[data_field_name + " (1)"], example_int_1d_array, example_unit, example_metadata
    )


@pytest.mark.parametrize("method", ["specific", "generic"])
@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(Axis))
def test_add_position(value, unit, metadata, transformation_type, method, example_base_component, request):
    """
    Validate that add_position and add_data_handler method from Components correctly
    add Axis object to its internal positions dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must add Axis within its position dictionary
        - Added Axis must be identified with the same name it was given during add_position method
        - Axis object within Component positions dictionary must be equivalent to how it was before insertion
    """

    # To avoid creating lots of different fixtures, manually create Axis DataHandler using Factory
    # if this test passes, other tests related to adding Axis, don't need to deal with all data types.
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)

    axis = AssonantDataHandlerFactory.create_axis(
        transformation_type=transformation_type,
        value=input_value,
        unit=input_unit,
        extra_metadata=input_metadata,
    )
    axis_name = "x"

    if method == "specific":
        target_method_ref = example_base_component.add_position
    if method == "generic":
        target_method_ref = example_base_component.add_data_handler

    target_method_ref(axis_name, axis.model_copy(deep=True))

    # Assert Axis was add to positions dict
    assert len(example_base_component.positions.items()) == 1

    # Assert correct name was given to Axis within positions dict and that it remained unchanged.
    assert_axis_equality(example_base_component.positions[axis_name], axis)


@pytest.mark.parametrize("method", ["specific", "generic"])
def test_add_position_with_name_conflict(
    example_base_component, example_translation_axis, example_rotation_axis, method
):
    """
    Validate that add_position and add_data_handler method from Components correctly add Axis object
    to its internal positions dictionary and handles name conflicts.

    Expected Behavior:
        - Both added Axis must be within Component positions internal dict
        - The first added Axis must not suffer any change from how it was before
        - Any subsequent Axis added that has the same name with another already existing Axis from the poisitions
        dict from Component must have its name automatically updated to a new unique name by adding an index in
        front the original passed name (e.g: <axis_name> (1))
    """
    axis_name = "x"

    if method == "specific":
        target_method_ref = example_base_component.add_position
    if method == "generic":
        target_method_ref = example_base_component.add_data_handler

    target_method_ref(axis_name, example_translation_axis.model_copy(deep=True))
    target_method_ref(axis_name, example_rotation_axis.model_copy(deep=True))

    # Assert both Axis objects were add to positions dict
    assert len(example_base_component.positions.items()) == 2

    # 1st Axis name and content must be unchanged
    assert_axis_equality(example_base_component.positions[axis_name], example_translation_axis)

    # 2nd Axis name must be the same as the 1st with an index due to name conflict and its content must be unchanged
    assert_axis_equality(example_base_component.positions[axis_name + " (1)"], example_rotation_axis)


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(Axis))
def test_add_position_methods_consistency(value, unit, metadata, transformation_type, example_base_component, request):
    """Validate that both add_positions and add_data_handler methods from Components result in
    the same outcome when adding Axis to Component.

    Expected Behavior:
        - Both added Axis must be within its respective positions internal dict
        - Both added Axis must be indentified with the same name within its respective position internal dict
        - Both added Axis must be equivalent
    """

    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)

    axis = AssonantDataHandlerFactory.create_axis(
        transformation_type=transformation_type,
        value=input_value,
        unit=input_unit,
        extra_metadata=input_metadata,
    )
    axis_name = "x"

    component_1 = example_base_component.model_copy(deep=True)
    component_2 = example_base_component

    component_1.add_position(axis_name, axis)
    component_2.add_data_handler(axis_name, axis)

    assert_axis_equality(component_1.positions[axis_name], component_2.positions[axis_name])


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(DataField))
def test_create_and_add_position(value, unit, metadata, transformation_type, example_base_component, request):
    """
    Validate that create_and_add_position method from Components correctly
    create and add Axis object to its internal positions dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must create a new Axis with passed data
        - Base Component must add the new created Axis within its positions dictionary
        - Added Axis must be identified with the same name it was given during create_and_add_position method
        - Axis object created by the Component must preserve passed data values.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_transformation_type = transformation_type

    axis_name = "x"

    example_base_component.create_and_add_position(
        axis_name, input_transformation_type, input_value, input_unit, input_metadata
    )

    # Assert created Axis was add to positions dict
    assert len(example_base_component.positions.items()) == 1

    # Assert correct name was given to Axis within positions dict and that it remained unchanged
    assert_axis_content(
        example_base_component.positions[axis_name], input_value, input_unit, input_metadata, input_transformation_type
    )


def test_create_and_add_position_with_name_conflict(
    example_float_1d_array, example_int_1d_array, example_unit, example_metadata, example_base_component
):
    """
    Validate that create_and_add_position method from Components correctly
    create and add Axis object to its internal positions dictionary and handles name conflict.

    Expected Behavior:
        - Both Axis DataHandlers must be created
        - Both created Axis must be add to Component positions dictionary
        - The first create and added Axis must have its name and content preserved
        - The second create and added Axis must have its content preserved but name updated
        to a new unique name by adding an index in front of the original anem (e.g: <axis_name> (1))
    """
    axis_name = "x"
    example_base_component.create_and_add_position(
        axis_name, TransformationType.TRANSLATION, example_float_1d_array, example_unit, example_metadata
    )
    example_base_component.create_and_add_position(
        axis_name, TransformationType.ROTATION, example_int_1d_array, example_unit, example_metadata
    )

    # Assert both created Axis were add to positions dict
    assert len(example_base_component.positions.items()) == 2

    # 1st Axis name and content must be unchanged
    assert_axis_content(
        example_base_component.positions[axis_name],
        example_float_1d_array,
        example_unit,
        example_metadata,
        TransformationType.TRANSLATION,
    )

    # 2nd Axis name must be the same as the 1st with an index due to name conflict and its content must be unchanged
    assert_axis_content(
        example_base_component.positions[axis_name + " (1)"],
        example_int_1d_array,
        example_unit,
        example_metadata,
        TransformationType.ROTATION,
    )


@pytest.mark.parametrize("method", ["specific", "generic"])
@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_add_timeseries_field(value, unit, metadata, timestamp, method, example_base_component, request):
    """
    Validate that add_timeseries_field and add_data_handler method from Components correctly
    add TimeSeries with DataField object to its internal fields dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must add passed TimeSeries within its fields dictionary
        - Added TimeSeries must be identified with the same name it was given during add_timeseries_field method
        - TimeSeries object within Component fields dictionary must be equivalent to how it was before insertion
    """

    # To avoid creating lots of different fixtures, manually create DataField DataHandler using Factory
    # if this test passes, other tests related to adding DataField, don't need to deal with all data types.
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_timestamp = get_fixture_values(timestamp, request)

    timeseries_data_field = AssonantDataHandlerFactory.create_timeseries_field(
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )
    timeseries_data_field_name = "timeseries_data_field"

    if method == "specific":
        target_method_ref = example_base_component.add_timeseries_field
    if method == "generic":
        target_method_ref = example_base_component.add_data_handler

    target_method_ref(timeseries_data_field_name, timeseries_data_field.model_copy(deep=True))

    # Assert TimeSeries with DataField was add to fields dict
    assert len(example_base_component.fields.items()) == 1

    # Assert correct name was given to DataField within fields dict and that it remained unchanged.
    assert_timeseries_equality(example_base_component.fields[timeseries_data_field_name], timeseries_data_field)


@pytest.mark.parametrize("method", ["specific", "generic"])
def test_add_timeseries_field_with_name_conflict(
    example_base_component, example_int_1d_timeseries_data_field, example_float_2d_timeseries_data_field, method
):
    """
    Validate that add_timeseries_field and add_data_handler method from Components correctly add TimeSeries
    object to its internal fields dictionary and handles name conflicts.

    Expected Behavior:
        - Both added TimeSeries must be within Component fields internal dict
        - The first added TimeSeries must not suffer any change from how it was before
        - Any subsequent TimeSeries added that has the same name with another already existing from the fields
        dict from Component must have its name automatically updated to a new unique name by adding an index in
        front the original passed name (e.g: <timeseries_field_name> (1))
    """
    timeseries_field_name = "timeseries_field_name"

    if method == "specific":
        target_method_ref = example_base_component.add_timeseries_field
    if method == "generic":
        target_method_ref = example_base_component.add_data_handler

    target_method_ref(timeseries_field_name, example_int_1d_timeseries_data_field.model_copy(deep=True))
    target_method_ref(timeseries_field_name, example_float_2d_timeseries_data_field.model_copy(deep=True))

    # Assert both DataField objects were add to positions dict
    assert len(example_base_component.fields.items()) == 2

    # 1st TimeSeries name and content must be unchanged
    assert_timeseries_equality(
        example_base_component.fields[timeseries_field_name], example_int_1d_timeseries_data_field
    )

    # 2nd TimeSeries name must be the same as the 1st with a index due to name conflict and
    # its content must be unchanged
    assert_timeseries_equality(
        example_base_component.fields[timeseries_field_name + " (1)"], example_float_2d_timeseries_data_field
    )


@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_add_timeseries_field_methods_consistency(value, unit, metadata, timestamp, example_base_component, request):
    """Validate that both add_timeseries_field and add_data_handler methods from Components result in
    the same outcome when adding TimeSeries with DataField value to Component.

    Expected Behavior:
        - Both added TimeSeries must be within its respective fields internal dict
        - Both added TimeSeries must be indentified with the same name within its respective fields internal dict
        - Both added TimeSeries must be equivalent
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_timestamp = get_fixture_values(timestamp, request)

    timeseries_field = AssonantDataHandlerFactory.create_timeseries_field(
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )
    timeseries_field_name = "timeseries_field_name"

    component_1 = example_base_component.model_copy(deep=True)
    component_2 = example_base_component

    component_1.add_timeseries_field(timeseries_field_name, timeseries_field)
    component_2.add_data_handler(timeseries_field_name, timeseries_field)

    assert_timeseries_equality(component_1.fields[timeseries_field_name], component_2.fields[timeseries_field_name])


@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_create_and_add_timeseries_field(value, unit, metadata, timestamp, example_base_component, request):
    """
    Validate that create_and_add_timeseries_field method from Components correctly
    add TimeSeries with DataField object to its internal fields dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must create a new TimeSeries within passed data
        - Base Component must add the new created TimeSeries within its fields dictionary
        - Added TimeSeries must be identified with the same name it was given during
        create_and_add_timeseries_field method
        - TimeSeries object created by the Component must preserve passed data values.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_timestamp = get_fixture_values(timestamp, request)

    timeseries_data_field_name = "timeseries_data_field"
    example_base_component.create_and_add_timeseries_field(
        name=timeseries_data_field_name,
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )

    # Assert TimeSeries with DataField was add to fields dict
    assert len(example_base_component.fields.items()) == 1

    # Assert correct name was given to DataField within fields dict and that it remained unchanged.
    assert_timeseries_content(
        example_base_component.fields[timeseries_data_field_name],
        input_value,
        input_unit,
        input_metadata,
        input_timestamp,
        input_unit,
        input_metadata,
    )


def test_create_and_add_timeseries_field_with_name_conflict(
    example_base_component, example_float_1d_array, example_int_1d_array, example_unit, example_metadata
):
    """
    Validate that create_and_add_timeseries_field method from Components correctly
    create and add TimeSeries object to its internal fields dictionary and handles name conflict.

    Expected Behavior:
        - Both TimeSeries must be created
        - Both created TimeSeries must be add to Component fields dictionary
        - The first created and added TimeSeries must have its name and content preserved
        - The second created and added TimeSeries must have its content preserved but name updated
        to a new unique name by adding an index in front of the original anem (e.g: <timeseries_data_field_name> (1))
    """
    timeseries_data_field_name = "timeseries_data_field"
    example_base_component.create_and_add_timeseries_field(
        timeseries_data_field_name,
        example_float_1d_array,
        example_float_1d_array,
        example_unit,
        example_metadata,
        example_unit,
        example_metadata,
    )
    example_base_component.create_and_add_timeseries_field(
        timeseries_data_field_name,
        example_int_1d_array,
        example_int_1d_array,
        example_unit,
        example_metadata,
        example_unit,
        example_metadata,
    )

    # Assert both created TimeSeries were add to fields dict
    assert len(example_base_component.fields.items()) == 2

    # 1st TimeSeries name and content must be unchanged
    assert_timeseries_content(
        example_base_component.fields[timeseries_data_field_name],
        example_float_1d_array,
        example_unit,
        example_metadata,
        example_float_1d_array,
        example_unit,
        example_metadata,
    )

    # 2nd TimeSeries name must be the same as the 1st with an index due to name conflict and
    # its content must be unchanged
    assert_timeseries_content(
        example_base_component.fields[timeseries_data_field_name + " (1)"],
        example_int_1d_array,
        example_unit,
        example_metadata,
        example_int_1d_array,
        example_unit,
        example_metadata,
    )


@pytest.mark.parametrize("method", ["specific", "generic"])
@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_add_timeseries_position(
    value, unit, metadata, timestamp, transformation_type, method, example_base_component, request
):
    """
    Validate that add_position and add_data_handler method from Components correctly add Axis
    object with TimeSeries to its internal positions dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must add Axis within its position dictionary
        - Added Axis must be identified with the same name it was given during add_position method
        - Axis object within Component positions dictionary must be equivalent to how it was before insertion
    """

    # To avoid creating lots of different fixtures, manually create Axis DataHandler with TimeSeries using Factory
    # if this test passes, other tests related to adding Axis, don't need to deal with all data types.
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_timestamp = get_fixture_values(timestamp, request)
    input_transformation_type = transformation_type

    timeseries_axis = AssonantDataHandlerFactory.create_timeseries_axis(
        transformation_type=input_transformation_type,
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )
    timeseries_axis_name = "x"

    if method == "specific":
        target_method_ref = example_base_component.add_position
    if method == "generic":
        target_method_ref = example_base_component.add_data_handler

    target_method_ref(timeseries_axis_name, timeseries_axis.model_copy(deep=True))

    # Assert Axis was add to positions dict
    assert len(example_base_component.positions.items()) == 1

    # Assert correct name was given to Axis within positions dict and that it remained unchanged.
    assert_axis_equality(example_base_component.positions[timeseries_axis_name], timeseries_axis)


@pytest.mark.parametrize("method", ["specific", "generic"])
def test_add_timeseries_position_with_name_conflict(
    example_base_component, example_timeseries_translation_axis, example_timeseries_rotation_axis, method
):
    """
    Validate that add_position and add_data_handler method from Components correctly add Axis with value
    represented as a TimeSeries to its internal positions dictionary and handles name conflicts.

    Expected Behavior:
        - Both added Axis must be within Component positions internal dict
        - The first added Axis must not suffer any change from how it was before
        - Any subsequent Axis added that has the same name with another already existing Axis from the poisitions
        dict from Component must have its name automatically updated to a new unique name by adding an index in
        front the original passed name (e.g: <timeseries_axis_name> (1))

    PS: Current expected behavior should be the same as just adding a normal position with name conflict, as Axis handle
    DataField or TimeSeries objects as its value field.
    """
    timeseries_axis_name = "x"

    if method == "specific":
        target_method_ref = example_base_component.add_position
    if method == "generic":
        target_method_ref = example_base_component.add_data_handler

    target_method_ref(timeseries_axis_name, example_timeseries_translation_axis.model_copy(deep=True))
    target_method_ref(timeseries_axis_name, example_timeseries_rotation_axis.model_copy(deep=True))

    # Assert both Axis objects were add to positions dict
    assert len(example_base_component.positions.items()) == 2

    # 1st Axis name and content must be unchanged
    assert_axis_equality(example_base_component.positions[timeseries_axis_name], example_timeseries_translation_axis)

    # 2nd Axis name must be the same as the 1st with an index due to name conflict and its content must be unchanged
    assert_axis_equality(
        example_base_component.positions[timeseries_axis_name + " (1)"], example_timeseries_rotation_axis
    )


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_add_timeseries_position_methods_consistency(
    value, unit, metadata, timestamp, transformation_type, example_base_component, request
):
    """Validate that both add_position and add_data_handler methods from Components result in
    the same outcome when adding Axis with TimeSeries value to Component.

    Expected Behavior:
        - Both added Axis must be within its respective positions internal dict
        - Both added Axis must be indentified with the same name within its respective positions internal dict
        - Both added Axis must be equivalent
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_timestamp = get_fixture_values(timestamp, request)
    input_transformation_type = transformation_type

    timeseries_axis = AssonantDataHandlerFactory.create_timeseries_axis(
        transformation_type=input_transformation_type,
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )
    timeseries_axis_name = "timeseries_axis"

    component_1 = example_base_component.model_copy(deep=True)
    component_2 = example_base_component

    component_1.add_position(timeseries_axis_name, timeseries_axis)
    component_2.add_data_handler(timeseries_axis_name, timeseries_axis)

    assert_axis_equality(component_1.positions[timeseries_axis_name], component_2.positions[timeseries_axis_name])


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_create_and_add_timeseries_position(
    value, unit, metadata, timestamp, transformation_type, example_base_component, request
):
    """
    Validate that create_and_add_timeseries_position method from Components correctly
    add Axis with TimeSeries object to its internal positions dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must create a new Axis with passed data
        - Base Component must add the new created Axis within its positions dictionary
        - Added Axis must be identified with the same name it was given during create_and_add_timeseries_position method
        - Axis object created by the Component must preserve passed data values.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_timestamp = get_fixture_values(timestamp, request)
    input_transformation_type = transformation_type

    timeseries_axis_name = "timeseries_axis"
    example_base_component.create_and_add_timeseries_position(
        name=timeseries_axis_name,
        transformation_type=input_transformation_type,
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )

    # Assert Axis was add to positions dict
    assert len(example_base_component.positions.items()) == 1

    # Assert correct name was given to Axis within positions dict and that it remained unchanged.
    assert_axis_content(
        example_base_component.positions[timeseries_axis_name],
        input_value,
        input_unit,
        input_metadata,
        transformation_type,
        input_timestamp,
        input_unit,
        input_metadata,
    )


def test_create_and_add_timeseries_position_with_name_conflict(
    example_base_component, example_float_1d_array, example_int_1d_array, example_unit, example_metadata
):
    """
    Validate that create_and_add_timeseries_position method from Components correctly
    create and add Axis object to its internal positions dictionary and handles name conflict.

    Expected Behavior:
        - Both Axis must be created
        - Both created Axis must be add to Component positions dictionary
        - The first created and added Axis must have its name and content preserved
        - The second created and added Axis must have its content preserved but name updated
        to a new unique name by adding an index in front of the original anem (e.g: <timeseries_axis_name> (1))
    """
    timeseries_axis_name = "timeseries_axis"
    example_base_component.create_and_add_timeseries_position(
        name=timeseries_axis_name,
        transformation_type=TransformationType.TRANSLATION,
        value=example_float_1d_array,
        timestamps=example_float_1d_array,
        unit=example_unit,
        extra_metadata=example_metadata,
        timestamps_unit=example_unit,
        timestamp_extra_metadata=example_metadata,
    )

    example_base_component.create_and_add_timeseries_position(
        name=timeseries_axis_name,
        transformation_type=TransformationType.ROTATION,
        value=example_int_1d_array,
        timestamps=example_int_1d_array,
        unit=example_unit,
        extra_metadata=example_metadata,
        timestamps_unit=example_unit,
        timestamp_extra_metadata=example_metadata,
    )

    # Assert both created Axis were add to fields dict
    assert len(example_base_component.positions.items()) == 2

    # 1st Axis name and content must be unchanged
    assert_axis_content(
        example_base_component.positions[timeseries_axis_name],
        example_float_1d_array,
        example_unit,
        example_metadata,
        TransformationType.TRANSLATION,
        example_float_1d_array,
        example_unit,
        example_metadata,
    )

    # 2nd TimeSeries name must be the same as the 1st with an index due to name conflict and
    # its content must be unchanged
    assert_axis_content(
        example_base_component.positions[timeseries_axis_name + " (1)"],
        example_int_1d_array,
        example_unit,
        example_metadata,
        TransformationType.ROTATION,
        example_int_1d_array,
        example_unit,
        example_metadata,
    )


def test_add_subcomponent(example_base_component, example_subcomponent):
    """
    Validate that add_subcomponent method from Components correctly
    add subcomponents to its internal dictionary.

    Expected Behavior:
        - Both added subcomponents must be within base_component internal sub_components dict
        - Added sub_components must be exactly equal to how it was before being add
    """
    example_subcomponent_2 = example_subcomponent.model_copy(deep=True)
    example_subcomponent_2.name = "new unique name"

    # Add copies to avoid that internal manipulation changes external data and causing possible False-Positive result.
    example_base_component.add_subcomponent(example_subcomponent.model_copy(deep=True))
    example_base_component.add_subcomponent(example_subcomponent_2.model_copy(deep=True))

    assert len(example_base_component.subcomponents.items()) == 2
    assert_component_equality(example_base_component.subcomponents[example_subcomponent.name], example_subcomponent)
    assert_component_equality(example_base_component.subcomponents[example_subcomponent_2.name], example_subcomponent_2)


def test_add_subcomponent_with_name_conflict(example_base_component, example_subcomponent):
    """
    Validate that add_subcomponent method from Components correctly
    handle cases where subcomponent with conflicting name are add.

    Expected Behavior:
        - Both added subcomponents must be within base_component internal sub_components dict
        - The first added sub_components must not suffer any change from how it was before
        - Any subsequent sub_component added that has the same name with another already existing subcomponent
        must have its name automatically updated to a new unique name by adding an index in front the original
        name (e.g: sub_component (1))
    """
    example_subcomponent_2 = example_subcomponent.model_copy(deep=True)

    example_base_component.add_subcomponent(example_subcomponent.model_copy(deep=True))
    example_base_component.add_subcomponent(example_subcomponent_2.model_copy(deep=True))

    assert len(example_base_component.subcomponents.items()) == 2

    # Assert that 1st subcomponent was totally unchanged
    assert_component_equality(example_base_component.subcomponents[example_subcomponent.name], example_subcomponent)

    with pytest.raises(AssertionError):
        # It is expected the assertion to fail, as subcomponent name should have been renamed,
        # otherwise name conflict handling failed
        assert_component_equality(
            example_base_component.subcomponents[example_subcomponent_2.name + " (1)"], example_subcomponent_2
        )

    # Assert it was only Component names that were different and caused previous AssertionError
    renamed_example_subcomponent_2 = example_subcomponent_2.model_copy(deep=True)
    renamed_example_subcomponent_2.name = example_base_component.subcomponents[
        example_subcomponent_2.name + " (1)"
    ].name
    assert_component_equality(
        example_base_component.subcomponents[example_subcomponent_2.name + " (1)"], renamed_example_subcomponent_2
    )


def test_add_list_of_subcomponents(example_base_component, example_subcomponent):
    """
    Validate that add_subcomponent method from Components correctly
    add list of subcomponents to its internal dictionary.

    Expected Behavior:
        - All added subcomponents must be within base_component internal sub_components dict
        - Added sub_components must be exactly equal to how it was before being add
    """
    example_subcomponent_2 = example_subcomponent.model_copy(deep=True)
    example_subcomponent_3 = example_subcomponent.model_copy(deep=True)
    example_subcomponent_2.name = "2nd subcomponent"
    example_subcomponent_3.name = "3rd subcomponent"

    list_of_subcomponents = [
        example_subcomponent.model_copy(deep=True),
        example_subcomponent_2.model_copy(deep=True),
        example_subcomponent_3.model_copy(deep=True),
    ]

    # Add copies to avoid that internal manipulation changes external data and causing possible False-Positive result.
    example_base_component.add_subcomponent(list_of_subcomponents)

    assert len(example_base_component.subcomponents.items()) == len(list_of_subcomponents)
    assert_component_equality(example_base_component.subcomponents[example_subcomponent.name], example_subcomponent)
    assert_component_equality(example_base_component.subcomponents[example_subcomponent_2.name], example_subcomponent_2)
    assert_component_equality(example_base_component.subcomponents[example_subcomponent_3.name], example_subcomponent_3)


def test_add_list_of_subcomponents_with_name_conflict(example_base_component, example_subcomponent):
    """
    Validate that add_subcomponent method from Components correctly handle cases where subcomponent
    with conflicting name exists inside subcomponents list being.

    Expected Behavior:
        - All added subcomponents must be within base_component internal sub_components dict
        - The first added sub_components must not suffer any change from how it was before
        - Any subsequent sub_component added that has the same name with another already existing subcomponent
        must have its name automatically updated to a new unique name by adding an index in front the original
        name (e.g: sub_component (1))
    """
    example_subcomponent_2 = example_subcomponent.model_copy(deep=True)
    example_subcomponent_3 = example_subcomponent.model_copy(deep=True)

    list_of_subcomponents = [
        example_subcomponent.model_copy(deep=True),
        example_subcomponent_2.model_copy(deep=True),
        example_subcomponent_3.model_copy(deep=True),
    ]

    # Add copies to avoid that internal manipulation changes external data and causing possible False-Positive result.
    example_base_component.add_subcomponent(list_of_subcomponents)

    assert len(example_base_component.subcomponents.items()) == len(list_of_subcomponents)

    # Assert that 1st subcomponent was totally unchanged
    assert_component_equality(example_base_component.subcomponents[example_subcomponent.name], example_subcomponent)

    with pytest.raises(AssertionError):
        # It is expected the assertion to fail, as subcomponent name should have been renamed,
        # otherwise name conflict handling failed
        assert_component_equality(
            example_base_component.subcomponents[example_subcomponent_2.name + " (1)"], example_subcomponent_2
        )

    # Assert it was only Component names that were different and caused previous AssertionError
    renamed_example_subcomponent_2 = example_subcomponent_2.model_copy(deep=True)
    renamed_example_subcomponent_2.name = example_base_component.subcomponents[
        example_subcomponent_2.name + " (1)"
    ].name
    assert_component_equality(
        example_base_component.subcomponents[example_subcomponent_2.name + " (1)"], renamed_example_subcomponent_2
    )

    with pytest.raises(AssertionError):
        # It is expected the assertion to fail, as subcomponent name should have been renamed,
        # otherwise name conflict handling failed
        assert_component_equality(
            example_base_component.subcomponents[example_subcomponent_3.name + " (2)"], example_subcomponent_3
        )

    # Assert it was only Component names that were different and caused previous AssertionError
    renamed_example_subcomponent_3 = example_subcomponent_3.model_copy(deep=True)
    renamed_example_subcomponent_3.name = example_base_component.subcomponents[
        example_subcomponent_3.name + " (2)"
    ].name
    assert_component_equality(
        example_base_component.subcomponents[example_subcomponent_3.name + " (2)"], renamed_example_subcomponent_3
    )


def test_component_take_data_handlers_from_single_component(
    example_base_component,
    example_int_1d_array_data_field,
    example_translation_axis,
    example_float_2d_timeseries_data_field,
    example_timeseries_rotation_axis,
):
    """
    Validate that take_data_handlers_from method from Components correctly take data_handlers
    from a single passed target Component.

    Expected Behavior:
        - All DataHandlers from target Component must be transfered to taker Component
        - Target Component fields and positions internal dicts must be empty after calling the method
        - Taker Component must have in its fields and positions internal dicts the taken DataHandlers
        - DataHandlers must be correctly stored in the correct taker Component internal dicts based in
        its type (Axis -> positions | TimeSeries and DataField -> fields)
        - Taken DataHandlers must be equivalent as they were before being taken
    """

    target_component = example_base_component.model_copy(deep=True)
    taker_component = example_base_component.model_copy(deep=True)

    data_field_name = "data_field"
    timeseries_data_field_name = "timeseries_data_field"
    axis_name = "axis"
    timeseries_axis_name = "timeseries_axis"
    target_component.add_data_handler(data_field_name, example_int_1d_array_data_field.model_copy(deep=True))
    target_component.add_data_handler(axis_name, example_translation_axis.model_copy(deep=True))
    target_component.add_data_handler(
        timeseries_data_field_name, example_float_2d_timeseries_data_field.model_copy(deep=True)
    )
    target_component.add_data_handler(timeseries_axis_name, example_timeseries_rotation_axis.model_copy(deep=True))

    # Check Component status before data handler takage
    assert len(target_component.fields) == 2 and len(target_component.positions) == 2
    assert len(taker_component.fields) == 0 and len(taker_component.positions) == 0

    taker_component.take_data_handlers_from(target_component)

    # Check Component status after data handler takage
    assert len(taker_component.fields) == 2 and len(taker_component.positions) == 2
    assert len(target_component.fields) == 0 and len(target_component.positions) == 0

    # Check if taken fields and positions haven't changed
    assert_data_fields_equality(taker_component.fields[data_field_name], example_int_1d_array_data_field)
    assert_axis_equality(taker_component.positions[axis_name], example_translation_axis)
    assert_timeseries_equality(
        taker_component.fields[timeseries_data_field_name], example_float_2d_timeseries_data_field
    )
    assert_axis_equality(taker_component.positions[timeseries_axis_name], example_timeseries_rotation_axis)


def test_component_take_data_handlers_from_list_of_components(
    example_base_component,
    example_int_1d_array_data_field,
    example_translation_axis,
    example_float_2d_timeseries_data_field,
    example_timeseries_rotation_axis,
):
    """
    Validate that take_data_handlers_from method from Components correctly take data_handlers
    from a list of target Components.

    Expected Behavior:
        - All DataHandlers from target Components must be transfered to taker Component
        - Target Components fields and positions internal dicts must be empty after calling the method
        - Taker Component must have in its fields and positions internal dicts the taken DataHandlers
        from all target Components
        - DataHandlers must be correctly stored in the correct taker Component internal dicts based in
        its type (Axis -> positions | TimeSeries and DataField -> fields)
        - Taken DataHandlers must be equivalent as they were before being taken
    """

    target_component_1 = example_base_component.model_copy(deep=True)
    target_component_2 = example_base_component.model_copy(deep=True)
    target_component_3 = example_base_component.model_copy(deep=True)
    target_component_4 = example_base_component.model_copy(deep=True)
    taker_component = example_base_component.model_copy(deep=True)

    data_field_name = "data_field"
    timeseries_data_field_name = "timeseries_data_field"
    axis_name = "axis"
    timeseries_axis_name = "timeseries_axis"
    target_component_1.add_data_handler(data_field_name, example_int_1d_array_data_field.model_copy(deep=True))
    target_component_2.add_data_handler(axis_name, example_translation_axis.model_copy(deep=True))
    target_component_3.add_data_handler(
        timeseries_data_field_name, example_float_2d_timeseries_data_field.model_copy(deep=True)
    )
    target_component_4.add_data_handler(timeseries_axis_name, example_timeseries_rotation_axis.model_copy(deep=True))

    # Check Components status before data handler takage
    assert len(target_component_1.fields) == 1 and len(target_component_1.positions) == 0
    assert len(target_component_2.fields) == 0 and len(target_component_2.positions) == 1
    assert len(target_component_3.fields) == 1 and len(target_component_3.positions) == 0
    assert len(target_component_4.fields) == 0 and len(target_component_4.positions) == 1
    assert len(taker_component.fields) == 0 and len(taker_component.positions) == 0

    components_list = [target_component_1, target_component_2, target_component_3, target_component_4]

    taker_component.take_data_handlers_from(components_list)

    # Check Components status after data handler takage
    assert len(target_component_1.fields) == 0 and len(target_component_1.positions) == 0
    assert len(target_component_2.fields) == 0 and len(target_component_2.positions) == 0
    assert len(target_component_3.fields) == 0 and len(target_component_3.positions) == 0
    assert len(target_component_4.fields) == 0 and len(target_component_4.positions) == 0
    assert len(taker_component.fields) == 2 and len(taker_component.positions) == 2

    # Check if taken fields and positions haven't changed
    assert_data_fields_equality(taker_component.fields[data_field_name], example_int_1d_array_data_field)
    assert_axis_equality(taker_component.positions[axis_name], example_translation_axis)
    assert_timeseries_equality(
        taker_component.fields[timeseries_data_field_name], example_float_2d_timeseries_data_field
    )
    assert_axis_equality(taker_component.positions[timeseries_axis_name], example_timeseries_rotation_axis)


def test_component_take_data_handlers_with_field_name_conflict(
    example_base_component, example_int_1d_array_data_field, example_float_2d_timeseries_data_field
):
    """
    Validate that take_data_handlers_from method from Components correctly take field data_handlers
    from a Component and handle name conflicts.

    Expected Behavior:
        - All DataHandlers from target Component must be transfered to taker Component even in case
        of name conflict
        - In the case of conflicts, the 1st field added to Component fields dict must be unaltered
        - Additional fields with conflicting names must be renamed by adding an index in front of
        the original name (e.g: <field_name> (1))
    """

    target_component = example_base_component.model_copy(deep=True)
    taker_component = example_base_component.model_copy(deep=True)

    data_field_name = "data_field"

    # Create a situation where field already exists on taker component and will receive a field with the same name
    taker_component.add_data_handler(data_field_name, example_int_1d_array_data_field.model_copy(deep=True))
    target_component.add_data_handler(data_field_name, example_float_2d_timeseries_data_field.model_copy(deep=True))

    taker_component.take_data_handlers_from(target_component)

    # Check if taken fields content haven't changed, except by taken field name
    assert_data_fields_equality(taker_component.fields[data_field_name], example_int_1d_array_data_field)
    assert_timeseries_equality(taker_component.fields[data_field_name + " (1)"], example_float_2d_timeseries_data_field)


def test_component_take_data_handlers_with_position_name_conflict(
    example_base_component, example_translation_axis, example_timeseries_rotation_axis
):
    """
    Validate that take_data_handlers_from method from Components correctly take position data_handlers
    from a Component and handle name conflicts.

    Expected Behavior:
        - All DataHandlers from target Component must be transfered to taker Component even in case
        of name conflict
        - In the case of conflicts, the 1st field added to Component fields dict must be unaltered
        - Additional fields with conflicting names must be renamed by adding an index in front of
        the original name (e.g: <field_name> (1))
    """

    target_component = example_base_component.model_copy(deep=True)
    taker_component = example_base_component.model_copy(deep=True)

    axis_name = "x"

    # Create a situation where position already exists on taker component and will receive a position with the same name
    taker_component.add_data_handler(axis_name, example_translation_axis.model_copy(deep=True))
    target_component.add_data_handler(axis_name, example_timeseries_rotation_axis.model_copy(deep=True))

    taker_component.take_data_handlers_from(target_component)

    # Check if taken fields content haven't changed, except by taken field name
    assert_axis_equality(taker_component.positions[axis_name], example_translation_axis)
    assert_axis_equality(taker_component.positions[axis_name + " (1)"], example_timeseries_rotation_axis)


def test_entry_take_data_handlers_from_single_entry(
    example_entry,
    example_int_1d_array_data_field,
    example_float_2d_timeseries_data_field,
):
    """
    Validate that take_data_handlers_from method from Entry correctly take data_handlers
    from a single passed target Entry.

    Expected Behavior:
        - All DataHandlers from target Entry must be transfered to taker Entry
        - Target Entry fields internal dict must be empty after calling the method
        - Taker Entry must have in its fields internal dict the taken DataHandlers
        - Taken DataHandlers must be equivalent as they were before being taken
    """

    target_entry = example_entry.model_copy(deep=True)
    target_entry_2 = example_entry.model_copy(deep=True)
    taker_entry = example_entry.model_copy(deep=True)

    data_field_name = "data_field"
    timeseries_data_field_name = "timeseries_data_field"

    target_entry.add_data_handler(data_field_name, example_int_1d_array_data_field.model_copy(deep=True))
    target_entry_2.add_data_handler(
        timeseries_data_field_name, example_float_2d_timeseries_data_field.model_copy(deep=True)
    )

    entries_list = [target_entry, target_entry_2]

    # Check Component status before data handler takage
    assert len(target_entry.fields) == 1
    assert len(target_entry_2.fields) == 1
    assert len(taker_entry.fields) == 0

    taker_entry.take_data_handlers_from(entries_list)

    # Check Component status after data handler takage
    assert len(target_entry.fields) == 0
    assert len(target_entry_2.fields) == 0
    assert len(taker_entry.fields) == 2

    # Check if taken fields and positions haven't changed
    assert_data_fields_equality(taker_entry.fields[data_field_name], example_int_1d_array_data_field)
    assert_timeseries_equality(taker_entry.fields[timeseries_data_field_name], example_float_2d_timeseries_data_field)


def test_entry_take_data_handlers_from_list_of_entries(
    example_entry,
    example_int_1d_array_data_field,
    example_float_2d_timeseries_data_field,
):
    """
    Validate that take_data_handlers_from method from Entry correctly take data_handlers
    from a passed list of Entries.

    Expected Behavior:
        - All DataHandlers from Entris within the list must be transfered to taker Entry
        - Target Entries fields internal dict must be empty after calling the method
        - Taker Entry must have in its fields internal dict the taken DataHandlers
        - Taken DataHandlers must be equivalent as they were before being taken
    """

    target_entry = example_entry.model_copy(deep=True)
    taker_entry = example_entry.model_copy(deep=True)

    data_field_name = "data_field"
    timeseries_data_field_name = "timeseries_data_field"

    target_entry.add_data_handler(data_field_name, example_int_1d_array_data_field.model_copy(deep=True))
    target_entry.add_data_handler(
        timeseries_data_field_name, example_float_2d_timeseries_data_field.model_copy(deep=True)
    )

    # Check Component status before data handler takage
    assert len(target_entry.fields) == 2
    assert len(taker_entry.fields) == 0

    taker_entry.take_data_handlers_from(target_entry)

    # Check Component status after data handler takage
    assert len(taker_entry.fields) == 2
    assert len(target_entry.fields) == 0

    # Check if taken fields and positions haven't changed
    assert_data_fields_equality(taker_entry.fields[data_field_name], example_int_1d_array_data_field)
    assert_timeseries_equality(taker_entry.fields[timeseries_data_field_name], example_float_2d_timeseries_data_field)


def test_entry_take_data_handlers_with_field_name_conflict(
    example_entry, example_int_1d_array_data_field, example_float_2d_timeseries_data_field
):
    """
    Validate that take_data_handlers_from method from Entry correctly take field data_handlers
    from a Entry and handle name conflicts.

    Expected Behavior:
        - All DataHandlers from target Entry must be transfered to taker Entry even in case
        of name conflict
        - In the case of conflicts, the 1st field added to Entry fields dict must be unaltered
        - Additional fields with conflicting names must be renamed by adding an index in front of
        the original name (e.g: <field_name> (1))
    """

    target_entry = example_entry.model_copy(deep=True)
    taker_entry = example_entry.model_copy(deep=True)

    data_field_name = "data_field"

    # Create a situation where field already exists on taker entry and will receive a field with the same name
    taker_entry.add_data_handler(data_field_name, example_int_1d_array_data_field.model_copy(deep=True))
    target_entry.add_data_handler(data_field_name, example_float_2d_timeseries_data_field.model_copy(deep=True))

    taker_entry.take_data_handlers_from(target_entry)

    # Check if taken fields content haven't changed, except by taken field name
    assert_data_fields_equality(taker_entry.fields[data_field_name], example_int_1d_array_data_field)
    assert_timeseries_equality(taker_entry.fields[data_field_name + " (1)"], example_float_2d_timeseries_data_field)
