"""Tests focused on validating AssonantDataHandler creation methods from Data Classes submodule"""

import pytest

from assonant.data_classes import AssonantDataHandlerFactory
from assonant.data_classes.data_handlers import Axis, DataField, TimeSeries
from assonant.data_classes.enums import TransformationType

from ..utils import (
    assert_axis_content,
    assert_axis_equality,
    assert_data_field_content,
    assert_data_fields_equality,
    assert_timeseries_content,
    assert_timeseries_equality,
    create_test_params_combinations,
    get_fixture_values,
)

# ================== Tests ==================


@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(DataField))
def test_data_field_creation_specific_method(value, unit, metadata, request):
    """
    Validate that AssonantDataHandlerFactory correctly creates DataField instances
    across a variety of input combinations over factory's specific creation method.

    Expected Behavior:
        - The factory method should:
            - Resolve `value`, `unit`, and `extra_metadata` inputs, which may vary from different types or None.
            - Instantiate a valid DataField with the provided attributes.
            - Preserve the data values passed.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)

    data_field = AssonantDataHandlerFactory.create_data_field(
        value=input_value, unit=input_unit, extra_metadata=input_metadata
    )

    assert_data_field_content(data_field, input_value, input_unit, input_metadata)


@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(DataField))
def test_data_field_creation_generic_method(value, unit, metadata, request):
    """
    Validate that AssonantDataHandlerFactory correctly creates DataField instances
    across a variety of input combinations over factory's generic creation method.

    Expected Behavior:
        - The factory method should:
            - Resolve `value`, `unit`, and `extra_metadata` inputs, which may vary from different types or None.
            - Instantiate a valid DataField with the provided attributes.
            - Preserve the data values passed.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)

    data_field = AssonantDataHandlerFactory.create_data_handler(
        value=input_value, unit=input_unit, extra_metadata=input_metadata
    )

    assert_data_field_content(data_field, input_value, input_unit, input_metadata)


@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(DataField))
def test_data_field_creation_methods_consistency(value, unit, metadata, request):
    """
    Validate that both AssonantDataHandlerFactory DataField creation methods
    return equal DataField instances. That guarantee consistency among creational
    methods.

    Expected Behavior:
        - Both factory methods must return equivalent DataField instances
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)

    data_field_from_specific_method = AssonantDataHandlerFactory.create_data_field(
        value=input_value, unit=input_unit, extra_metadata=input_metadata
    )

    data_field_from_generic_method = AssonantDataHandlerFactory.create_data_handler(
        value=input_value, unit=input_unit, extra_metadata=input_metadata
    )

    assert_data_fields_equality(data_field_from_specific_method, data_field_from_generic_method)


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(Axis))
def test_axis_creation_specific_method(value, unit, metadata, transformation_type, request):
    """
    Validate that AssonantDataHandlerFactory correctly creates Axis instances
    across a variety of input combinations over factory's specific creation method.

    Expected Behavior:
        - The factory method should:
            - Resolve `value`, `unit`, `extra_metadata` ans `transformation_type` inputs,
            which may vary from different types or None.
            - Instantiate a valid Axis with the provided attributes.
            - Axis value property must be a valid DataField with the provided attributes.
            - Preserve the data values passed.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_transformation_type = transformation_type

    axis = AssonantDataHandlerFactory.create_axis(
        transformation_type=input_transformation_type,
        value=input_value,
        unit=input_unit,
        extra_metadata=input_metadata,
    )

    assert_axis_content(axis, input_value, input_unit, input_metadata, transformation_type)


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(Axis))
def test_axis_creation_generic_method(value, unit, metadata, transformation_type, request):
    """
    Validate that AssonantDataHandlerFactory correctly creates Axis instances
    across a variety of input combinations over factory's generic creation method.

    Expected Behavior:
        - The factory method should:
            - Resolve `value`, `unit`, `extra_metadata` ans `transformation_type` inputs,
            which may vary from different types or None.
            - Instantiate a valid Axis with the provided attributes.
            - Axis value property must be a valid DataField with the provided attributes.
            - Preserve the data values passed.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_transformation_type = transformation_type

    axis = AssonantDataHandlerFactory.create_data_handler(
        transformation_type=input_transformation_type,
        value=input_value,
        unit=input_unit,
        extra_metadata=input_metadata,
    )

    assert_axis_content(axis, input_value, input_unit, input_metadata, transformation_type)


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(Axis))
def test_axis_creation_methods_consistency(value, unit, metadata, transformation_type, request):
    """
    Validate that both AssonantDataHandlerFactory Axis creation methods
    return equal Axis instances. That guarantee consistency among creational
    methods.

    Expected Behavior:
        - Both factory methods must return equivalent Axis instances
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_transformation_type = transformation_type

    axis_from_specific_method = AssonantDataHandlerFactory.create_axis(
        transformation_type=input_transformation_type,
        value=input_value,
        unit=input_unit,
        extra_metadata=input_metadata,
    )

    axis_from_generic_method = AssonantDataHandlerFactory.create_data_handler(
        transformation_type=input_transformation_type,
        value=input_value,
        unit=input_unit,
        extra_metadata=input_metadata,
    )

    assert_axis_equality(axis_from_specific_method, axis_from_generic_method)


@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_timeseries_field_creation_specific_method(value, unit, metadata, timestamp, request):
    """
    Validate that AssonantDataHandlerFactory correctly creates TimeSeries instances
    across a variety of input combinations over factory's specific creation method.

    Expected Behavior:
        - The factory method should:
            - Resolve `value`, `unit`, and `extra_metadata` inputs, which may vary from different types or None.
            - Instantiate a valid TimeSeries with the provided attributes.
            - TimeSeries value and timestamp properties must be valid DataFields with the provided attributes.
            - Preserve the data values passed.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_timestamp = get_fixture_values(timestamp, request)

    timeseries = AssonantDataHandlerFactory.create_timeseries_field(
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )

    assert_timeseries_content(
        timeseries, input_value, input_unit, input_metadata, input_timestamp, input_unit, input_metadata
    )


@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_timeseries_field_creation_generic_method(value, unit, metadata, timestamp, request):
    """
    Validate that AssonantDataHandlerFactory correctly creates TimeSeries instances
    across a variety of input combinations over factory's generic creation method.

    Expected Behavior:
        - The factory method should:
            - Resolve `value`, `unit`, and `extra_metadata` inputs, which may vary from different types or None.
            - Instantiate a valid TimeSeries with the provided attributes.
            - TimeSeries value and timestamp properties must be valid DataFields with the provided attributes.
            - Preserve the data values passed.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_timestamp = get_fixture_values(timestamp, request)

    timeseries = AssonantDataHandlerFactory.create_data_handler(
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )
    assert_timeseries_content(
        timeseries, input_value, input_unit, input_metadata, input_timestamp, input_unit, input_metadata
    )


@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_timeseries_field_creation_methods_consistency(value, unit, metadata, timestamp, request):
    """
    Validate that both AssonantDataHandlerFactory TimeSeries with DataField creation methods
    return equal TimeSeries instances. That guarantee consistency among creational
    methods.

    Expected Behavior:
        - Both factory methods must return equivalent TimeSeries instances with DataField DataHandlers.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_timestamp = get_fixture_values(timestamp, request)

    timeseries_from_specific_method = AssonantDataHandlerFactory.create_timeseries_field(
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )

    timeseries_from_generic_method = AssonantDataHandlerFactory.create_data_handler(
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )

    assert_timeseries_equality(timeseries_from_specific_method, timeseries_from_generic_method)


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_timeseries_axis_creation_specific_method(value, unit, metadata, timestamp, transformation_type, request):
    """
    Validate that AssonantDataHandlerFactory correctly creates Axis instances with TimeSeries
    data instances across a variety of input combinations over factory's specifc creation method
    to create Axis instances with TimeSeries.

    Expected Behavior:
        - The factory method should:
            - Resolve `value`, `unit`, and `extra_metadata` inputs, which may vary from different types or None.
            - Instantiate a valid Axis with the provided attributes.
            - Axis value property must be a valid TimeSeries with the provided attributes.
            - Preserve the data values passed.
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

    assert_axis_content(
        timeseries_axis,
        input_value,
        input_unit,
        input_metadata,
        input_transformation_type,
        input_timestamp,
        input_unit,
        input_metadata,
    )


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_timeseries_axis_creation_generic_method(value, unit, metadata, timestamp, transformation_type, request):
    """
    Validate that AssonantDataHandlerFactory correctly creates Axis instances with TimeSeries
    data instances across a variety of input combinations over factory's generic creation method
    to create Axis instances with TimeSeries.

    Expected Behavior:
        - The factory method should:
            - Resolve `value`, `unit`, and `extra_metadata` inputs, which may vary from different types or None.
            - Instantiate a valid Axis with the provided attributes.
            - Axis value property must be a valid TimeSeries with the provided attributes.
            - Preserve the data values passed.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_timestamp = get_fixture_values(timestamp, request)
    input_transformation_type = transformation_type

    timeseries_axis = AssonantDataHandlerFactory.create_data_handler(
        transformation_type=input_transformation_type,
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )

    assert_axis_content(
        timeseries_axis,
        input_value,
        input_unit,
        input_metadata,
        input_transformation_type,
        input_timestamp,
        input_unit,
        input_metadata,
    )


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata, timestamp", create_test_params_combinations(TimeSeries))
def test_timeseries_axis_creation_methods_consistency(value, unit, metadata, timestamp, transformation_type, request):
    """
    Validate that both AssonantDataHandlerFactory Axis with TimeSeries DataHandlers creation methods
    return equal Axis with TimeSeries instances. That guarantee consistency among creational
    methods.

    Expected Behavior:
        - Both factory methods must return equivalent Axis instances with TimeSeries DataHandlers.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_timestamp = get_fixture_values(timestamp, request)
    input_transformation_type = transformation_type

    timeseries_axis_from_specific_method = AssonantDataHandlerFactory.create_data_handler(
        transformation_type=input_transformation_type,
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )

    timeseries_axis_from_generic_method = AssonantDataHandlerFactory.create_timeseries_axis(
        transformation_type=input_transformation_type,
        value=input_value,
        timestamps=input_timestamp,
        unit=input_unit,
        extra_metadata=input_metadata,
        timestamps_unit=input_unit,
        timestamp_extra_metadata=input_metadata,
    )

    assert_axis_equality(timeseries_axis_from_specific_method, timeseries_axis_from_generic_method)
