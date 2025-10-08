import importlib
import inspect
from pathlib import Path
from typing import List

import pytest
from nexusformat.nexus.tree import (
    NXentry,
    NXfield,
    NXgroup,
    NXinstrument,
    NXlog,
    NXtransformations,
    nxload,
)

from assonant.data_classes.components import Component
from assonant.data_classes.data_handlers import Axis, DataField, TimeSeries
from assonant.file_writer import AssonantFileWriter
from assonant.file_writer.exceptions import FileWriterFactoryError
from assonant.file_writer.file_writer_factory import FileWriterFactory

from ..utils import (
    assert_nxobject_and_assonant_axis_equality,
    assert_nxobject_and_assonant_data_field_equality,
    get_fixture_values,
    get_list_of_data_handlers_fixture_names,
)


@pytest.fixture(scope="session")
def nexus_file_writer() -> AssonantFileWriter:
    return AssonantFileWriter(file_format="nexus")


@pytest.fixture(scope="function")
def base_tmp_dir_path(tmp_path_factory) -> str:
    return str(tmp_path_factory.mktemp("test"))


def get_components_name_from_assonant_submodule() -> List[Component]:
    """
    Return a list with all names from existing Component classes within Components
    submodule from Assonant Data Classes.

    Returns:
        List[Component]: List with all existing Component class names within
        Components submodule from Assonant Data Classes.
    """
    return [
        member[0]
        for member in inspect.getmembers(importlib.import_module("assonant.data_classes.components"), inspect.isclass)
    ]


def test_invalid_file_format():
    """
    Validate that AssonantFileWriter constructor correctly raises exception
    if unsupported file_format is passed during object construction.

    Expected Behavior:
        - AssonantFileWriter must raise an FileWriterFactoryError if an unsupported file format is passed.
    """
    with pytest.raises(FileWriterFactoryError):
        _ = AssonantFileWriter(file_format="UNSUPPORTED_FILE_FORMAT")


def test_get_supported_file_formats():
    """
    Validate that AssonantFileWriter correctly return supported file formats.

    Expected Behavior:
        - AssonantFileWriter method must return a list of formats equal to the
        supported formats by the FileWriterFactory.
    """
    assert AssonantFileWriter.get_supported_file_formats() == FileWriterFactory.get_supported_file_formats()


def test_get_file_extension(nexus_file_writer):
    """
    Validate that AssonantFileWriter correctly return correct file extension.

    Expected Behavior:
        - AssonantFileWriter method must return the same file extension defined by the format specific
        file writer.
    """
    assert nexus_file_writer.get_file_extension() == nexus_file_writer.file_writer.get_file_extension()


@pytest.mark.parametrize(
    "component_name",
    [c_name for c_name in get_components_name_from_assonant_submodule() if c_name not in ["Beamline", "Component"]],
)
def test_write_component_as_nexus_group(
    nexus_file_writer, base_tmp_dir_path, example_components_collection, component_name, component_to_nexus_mapping
):
    """
    Validate that AssonantFileWriter correctly create NeXus groups related to passed
    Assonant data classes Component within NeXus files.

    PS: Beamline is a special case treated in a standalone test

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the same name as the one given to the component must be created within the file
        - The group must be in the root level of the nexus hierarchy
    """
    filename = "test_nexus"
    empty_component = example_components_collection[component_name]
    component_nexus_type = component_to_nexus_mapping[type(empty_component)]
    group_name = component_name.lower()

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=empty_component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    nxroot = nxload(output_file_path, mode="r")

    # Check group was created with component name and fits the correct NeXus object
    assert nxroot[group_name]
    assert isinstance(nxroot[group_name], NXgroup)
    assert nxroot[group_name].nxclass
    assert isinstance(nxroot[group_name], component_nexus_type)


def test_write_beamline_component_special_case_as_nexus_group(nexus_file_writer, base_tmp_dir_path, example_entry):
    """
    Validate that AssonantFileWriter correctly write Assonant data classes Beamline specific case within NeXus files.

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the name instrument must be created within the NeXus file
        - This group must be of NXinstrument type
        - This group must have a field called name with value equivalent to the Beamline name value
        - The group must be in the root level of the nexus hierarchy
    """
    filename = "test_nexus"
    empty_beamline = example_entry.beamline

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=empty_beamline)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    nxroot = nxload(output_file_path, mode="r")

    # Check group was correctly created within NeXus file
    assert nxroot["instrument"]
    assert isinstance(nxroot["instrument"], NXinstrument)


def test_write_entry_as_nexus_group(nexus_file_writer, base_tmp_dir_path, example_entry):
    """
    Validate that AssonantFileWriter correctly write Assonant data classes Entry within NeXus files.

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the same name as the one given to the Entry must be created within the file
        - The group must be in the root level of the nexus hierarchy
        - The group.nxclass attribute just be NXentry
        - The Entry must have an group within it named instrument
        - The instrument.nxclass attribute must be NXinstrument
        - The instrument.name field must have the same value as Entry's Beamline name.
    """
    filename = "test_nexus"

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=example_entry)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    nxroot = nxload(output_file_path, mode="r")

    # Check entry was correctly created
    assert nxroot[example_entry.name]
    assert isinstance(nxroot[example_entry.name], NXgroup)
    assert isinstance(nxroot[example_entry.name], NXentry)
    # Check instrument was correctly created
    assert nxroot[example_entry.name]["instrument"]
    assert isinstance(nxroot[example_entry.name]["instrument"], NXinstrument)
    assert nxroot[example_entry.name]["instrument"].name == example_entry.beamline.fields["name"].value


@pytest.mark.parametrize(
    "example_data_field_fixture_name", get_list_of_data_handlers_fixture_names(data_handler_type=DataField)
)
def test_write_component_field_as_nexus_field(
    nexus_file_writer, base_tmp_dir_path, example_components_collection, example_data_field_fixture_name, request
):
    """
    Validate that AssonantFileWriter correctly write Assonant Component field as a NeXus field within its
    respective group in the NeXus file.

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the same name as the device must be created
        - Inside the device group, data fields must exist with the respective given name with the same values
        they had before being written to the file.
    """
    filename = "test_nexus"
    component_name = "Mirror"
    component = example_components_collection[
        component_name
    ]  # Any Component fits this test as it isn't the tested featured.
    group_name = component_name.lower()

    example_data_field = get_fixture_values(example_data_field_fixture_name, request)

    component.add_field(example_data_field_fixture_name, example_data_field)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())

    # Check file was created
    assert output_file_path.exists()

    nxroot = nxload(output_file_path, mode="r")

    # Check nexus content and structure is correct
    assert nxroot[group_name][example_data_field_fixture_name]
    assert isinstance(nxroot[group_name][example_data_field_fixture_name], NXfield)
    assert_nxobject_and_assonant_data_field_equality(
        nxroot[group_name][example_data_field_fixture_name], example_data_field
    )


@pytest.mark.parametrize(
    "example_data_field_fixture_name", get_list_of_data_handlers_fixture_names(data_handler_type=DataField)
)
def test_write_beamline_component_field_as_nexus_field(
    nexus_file_writer, base_tmp_dir_path, example_entry, example_data_field_fixture_name, request
):
    """
    Validate that AssonantFileWriter correctly write Assonant Beamline Component field as a NeXus field within its
    respective group in the NeXus file.

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group named instrument must be created to store Beamline information
        - Inside the instrument group, data fields must exist with the respective given name with the same values
        they had before being written to thefile.
    """
    filename = "test_nexus"
    component = example_entry.beamline
    group_name = "instrument"  # Beamline specific case

    example_data_field = get_fixture_values(example_data_field_fixture_name, request)

    component.add_field(example_data_field_fixture_name, example_data_field)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())

    # Check file was created
    assert output_file_path.exists()

    nxroot = nxload(output_file_path, mode="r")

    # Check nexus content and structure is correct
    assert nxroot[group_name][example_data_field_fixture_name]
    assert isinstance(nxroot[group_name][example_data_field_fixture_name], NXfield)
    assert_nxobject_and_assonant_data_field_equality(
        nxroot[group_name][example_data_field_fixture_name], example_data_field
    )


@pytest.mark.parametrize(
    "example_data_field_fixture_name", get_list_of_data_handlers_fixture_names(data_handler_type=DataField)
)
def test_write_entry_field_as_nexus_field(
    nexus_file_writer, base_tmp_dir_path, example_entry, example_data_field_fixture_name, request
):
    """
    Validate that AssonantFileWriter correctly write Assonant Beamline Component field as a NeXus field within its
    respective group in the NeXus file.

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group named instrument must be created to store Beamline information
        - Inside the instrument group, data fields must exist with the respective given name with the same values
        they had before being written to thefile.
    """
    filename = "test_nexus"

    example_data_field = get_fixture_values(example_data_field_fixture_name, request)

    entry_name = example_entry.name
    example_entry.add_field(example_data_field_fixture_name, example_data_field)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=example_entry)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())

    # Check file was created
    assert output_file_path.exists()

    nxroot = nxload(output_file_path, mode="r")

    # Check nexus content and structure is correct
    assert nxroot[entry_name][example_data_field_fixture_name]
    assert isinstance(nxroot[entry_name][example_data_field_fixture_name], NXfield)
    assert_nxobject_and_assonant_data_field_equality(
        nxroot[entry_name][example_data_field_fixture_name], example_data_field
    )


@pytest.mark.parametrize("example_axis_fixture_name", get_list_of_data_handlers_fixture_names(data_handler_type=Axis))
def test_write_component_position_as_nexus_field(
    nexus_file_writer, base_tmp_dir_path, example_components_collection, example_axis_fixture_name, request
):
    """
    Validate that AssonantFileWriter correctly write Assonant Component position as a NeXus field within its
    Component's respective NXtransformation group.

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the same name as the device must be created
        - Inside the device group, a group called 'transformations' must be create
        - The 'transformations' group must be of NXtransformation type
        - Inside the 'transformations' group axis information must exist as NXfield with the respective given
          name with the same values they had before being written to the file.
    """
    filename = "test_nexus"
    component_name = "Mirror"
    component = example_components_collection[
        component_name
    ]  # Any Component fits this test as it isn't the tested featured.
    group_name = component_name.lower()

    example_axis = get_fixture_values(example_axis_fixture_name, request)

    component.add_position(example_axis_fixture_name, example_axis)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())

    # Check file was created
    assert output_file_path.exists()

    nxroot = nxload(output_file_path, mode="r")

    # Check if transformation group was created
    assert nxroot[group_name]["transformations"]
    assert isinstance(nxroot[group_name]["transformations"], NXtransformations)

    # Check if transformation group content is correct
    assert nxroot[group_name]["transformations"][example_axis_fixture_name]
    assert isinstance(nxroot[group_name]["transformations"][example_axis_fixture_name], NXfield)
    assert_nxobject_and_assonant_axis_equality(
        nxroot[group_name]["transformations"][example_axis_fixture_name], example_axis
    )


# ===================== Warning =========================
# | TEST WRITE BEAMLINE POSITION WAS NOT IMPLEMENTED    |
# | AS THIS IS A UNDESIRED BEHAVIOR FUTURALLY, BEAMLINE |
# | COMPONENT MUST PROHIBIT ADDING POSITION TO IT AND A |
# | TEST TO VALIDATE IT MUST BE DONE                    |
# =======================================================


@pytest.mark.parametrize(
    "example_timeseries_fixture_name", get_list_of_data_handlers_fixture_names(data_handler_type=TimeSeries)
)
def test_write_component_timeseries_field_as_nexus_field(
    nexus_file_writer, base_tmp_dir_path, example_components_collection, example_timeseries_fixture_name, request
):
    """
    Validate that AssonantFileWriter correctly write Assonant Component timeseries as NeXus fields within its
    Component's respective group.

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the same name as the device must be created
        - Inside the device group, a group with the name of the field must be create
        - The group with the field name must be of 'NXlog' type
        - Inside the group with the field name two NXfield must exist:
            - (1) 'value' field must store the same data as the TimeSeries value property
            - (2) 'time' field must store the same data as the TimeSeries timestamps property
        - If the Datahandler is actually an Axis with TimeSeries DataField, the same behavior
        is expected but inside the NXtransformation group
    """
    filename = "test_nexus"

    component_name = "Mirror"
    component = example_components_collection[
        component_name
    ]  # Any Component fits this test as it isn't the tested featured.
    group_name = component_name.lower()

    example_timeseries = get_fixture_values(example_timeseries_fixture_name, request)

    component.add_data_handler(example_timeseries_fixture_name, example_timeseries)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())

    # Check file was created
    assert output_file_path.exists()

    nxroot = nxload(output_file_path, mode="r")

    # Check fixture tyṕe is correct to avoid bypassing test
    assert isinstance(example_timeseries, TimeSeries) or isinstance(example_timeseries, Axis)

    # Check nexus content and structure is correct relative to the time of TimeSeries
    if isinstance(example_timeseries, TimeSeries):
        timeseries_path = "/".join([group_name, example_timeseries_fixture_name])
        assertion_method = assert_nxobject_and_assonant_data_field_equality
        relative_data_field_ref = example_timeseries.value
        relative_timestamps_ref = example_timeseries.timestamps
    elif isinstance(example_timeseries, Axis):
        timeseries_path = "/".join([group_name, "transformations", example_timeseries_fixture_name])
        assertion_method = assert_nxobject_and_assonant_axis_equality
        relative_data_field_ref = example_timeseries
        relative_timestamps_ref = example_timeseries.value.timestamps

    assert nxroot[timeseries_path]
    assert isinstance(nxroot[timeseries_path], NXlog)
    assert nxroot[timeseries_path]["value"]
    assert isinstance(nxroot[timeseries_path]["value"], NXfield)
    assert nxroot[timeseries_path]["time"]
    assert isinstance(nxroot[timeseries_path]["time"], NXfield)

    assertion_method(nxroot[timeseries_path]["value"], relative_data_field_ref)
    assert_nxobject_and_assonant_data_field_equality(nxroot[timeseries_path]["time"], relative_timestamps_ref)


@pytest.mark.parametrize(
    "subcomponent_name",
    [c_name for c_name in get_components_name_from_assonant_submodule() if c_name not in ["Beamline", "Component"]],
)
def test_write_subcomponent_as_nexus_group(
    nexus_file_writer, base_tmp_dir_path, example_components_collection, subcomponent_name, component_to_nexus_mapping
):
    """
    Validate that AssonantFileWriter correctly create NeXus groups related to passed
    Assonant data classes Component and its subcomponent within NeXus files.

    PS: Beamline is a special case treated in a standalone test

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the same name as the one given to the component must be created within the file
        - A group within the component group must be created with the name name as the subcomponent
        - The subgroup nexus class must fit the respective NeXus class for the subcomponent type
    """
    filename = "test_nexus"
    component_name = "Monochromator"  # Don't matter which component is used as subcomponents are the focus
    empty_component = example_components_collection[component_name].__deepcopy__()  # deepcopy to avoid infinite loop
    empty_subcomponent = example_components_collection[subcomponent_name]
    subcomponent_nexus_type = component_to_nexus_mapping[type(empty_subcomponent)]
    component_group_name = component_name.lower()
    subcomponent_group_name = subcomponent_name.lower()

    empty_component.add_subcomponent(empty_subcomponent)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=empty_component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    nxroot = nxload(output_file_path, mode="r")

    # Check subgroup was created with subcomponent name and with correct Nexus type
    assert nxroot[component_group_name][subcomponent_group_name]
    assert isinstance(nxroot[component_group_name][subcomponent_group_name], NXgroup)
    assert nxroot[component_group_name][subcomponent_group_name].nxclass
    assert isinstance(nxroot[component_group_name][subcomponent_group_name], subcomponent_nexus_type)


def test_write_beamline_subcomponent_as_nexus_group(
    nexus_file_writer, base_tmp_dir_path, example_components_collection
):
    """
    Validate that AssonantFileWriter correctly create NeXus groups related to passed
    Assonant data classes Beamline Component and its subcomponent within NeXus files.

    PS: No need to test all subcomponent types as they were already tested on previous test

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the name 'instrument' must be created within the file for the Beamline Component
        - A group within the 'instrument' group must be created with the name name as the subcomponent
    """
    filename = "test_nexus"
    component_name = "Beamline"
    subcomponent_name = "Mirror"
    empty_component = example_components_collection[component_name]
    empty_subcomponent = example_components_collection[subcomponent_name]
    component_group_name = "instrument"
    subcomponent_group_name = subcomponent_name.lower()

    empty_component.add_subcomponent(empty_subcomponent)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=empty_component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    nxroot = nxload(output_file_path, mode="r")

    # Check subgroup was created with subcomponent name and with correct Nexus type
    assert nxroot[component_group_name][subcomponent_group_name]
    assert isinstance(nxroot[component_group_name][subcomponent_group_name], NXgroup)
    assert nxroot[component_group_name][subcomponent_group_name].nxclass


def test_write_data_field_within_subcomponent_as_nexus_field(
    nexus_file_writer, base_tmp_dir_path, example_components_collection, example_int_1d_array_data_field
):
    """
    Validate that AssonantFileWriter correctly save subcomponent data field within NeXus file

    PS: Don't need to extensively test data types as that was already tested on previous tests.

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the same name as the one given to the component must be created within the file
        - A group within the component group must be created with the name as the subcomponent
        - A nexus field must exist within the subcomponent group with its content equivalent
        to Assonant DataField
    """
    filename = "test_nexus"
    component_name = "Monochromator"  # Don't matter which componet is used as subcomponents are the focus
    subcomponent_name = "Mirror"
    data_field_name = "data_field"
    component = example_components_collection[component_name]
    subcomponent = example_components_collection[subcomponent_name]
    component_group_name = component_name.lower()
    subcomponent_group_name = subcomponent_name.lower()

    subcomponent.add_field(data_field_name, example_int_1d_array_data_field)
    component.add_subcomponent(subcomponent)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    nxroot = nxload(output_file_path, mode="r")

    path_to_nxfield = "/".join([component_group_name, subcomponent_group_name, data_field_name])

    # Check subgroup was created with subcomponent name and with correct Nexus type
    assert nxroot[path_to_nxfield]
    assert isinstance(nxroot[path_to_nxfield], NXfield)
    assert_nxobject_and_assonant_data_field_equality(nxroot[path_to_nxfield], example_int_1d_array_data_field)


def test_write_axis_within_subcomponent_as_nexus_field(
    nexus_file_writer, base_tmp_dir_path, example_components_collection, example_translation_axis
):
    """
    Validate that AssonantFileWriter correctly save subcomponent axis within NeXus file

    PS: Don't need to extensively test data types as that was already tested on previous tests.

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the same name as the one given to the component must be created within the file
        - A group within the component group must be created with the name as the subcomponent
        - A group within the subcomponent group named 'transformations' must be created
        - A nexus field must exist within the 'transformation' group with its name and content equivalent
        to Assonant Axis
    """
    filename = "test_nexus"
    component_name = "Monochromator"  # Don't matter which componet is used as subcomponents are the focus
    subcomponent_name = "Mirror"
    axis_name = "axis_name"
    component = example_components_collection[component_name]
    subcomponent = example_components_collection[subcomponent_name]
    component_group_name = component_name.lower()
    subcomponent_group_name = subcomponent_name.lower()

    subcomponent.add_position(axis_name, example_translation_axis)
    component.add_subcomponent(subcomponent)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    nxroot = nxload(output_file_path, mode="r")

    path_to_nxfield = "/".join([component_group_name, subcomponent_group_name, "transformations", axis_name])

    # Check subgroup was created with subcomponent name and with correct Nexus type
    assert nxroot[path_to_nxfield]
    assert isinstance(nxroot[path_to_nxfield], NXfield)
    assert_nxobject_and_assonant_axis_equality(nxroot[path_to_nxfield], example_translation_axis)


def test_write_data_field_timeseries_within_subcomponent_as_nexus_field(
    nexus_file_writer, base_tmp_dir_path, example_components_collection, example_int_1d_timeseries_data_field
):
    """
    Validate that AssonantFileWriter correctly save TimeSeries DataField within NeXus file

    PS: Don't need to extensively test data types as that was already tested on previous tests.

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the same name as the one given to the component must be created within the file
        - A group within the component group must be created with the name as the subcomponent
        - A group within the subcomponent group with the same name as the TimeSeries DataHandler must be created
        - The TimeSeries DataHandler group must be of type NXlog
        - Two nexus fields must exist within the TimeSeries group:
            (1) 'value': nexus field storing value property from the TimeSeries
            (2) 'time': nexus field storing timestamps property from the TimeSeries]
        - The TimeSeries group content must be equivalent to Assonant TimeSeries DataHandler
    """
    filename = "test_nexus"
    component_name = "Monochromator"  # Don't matter which componet is used as subcomponents are the focus
    subcomponent_name = "Mirror"
    timeseries_data_field_name = "timeseries_data_field"
    component = example_components_collection[component_name]
    subcomponent = example_components_collection[subcomponent_name]
    component_group_name = component_name.lower()
    subcomponent_group_name = subcomponent_name.lower()

    subcomponent.add_timeseries_field(timeseries_data_field_name, example_int_1d_timeseries_data_field)
    component.add_subcomponent(subcomponent)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    nxroot = nxload(output_file_path, mode="r")

    path_to_value_nxfield = "/".join(
        [component_group_name, subcomponent_group_name, timeseries_data_field_name, "value"]
    )
    path_to_time_nxfield = "/".join([component_group_name, subcomponent_group_name, timeseries_data_field_name, "time"])

    # Check subgroup was created with subcomponent name and with correct Nexus type
    assert nxroot[path_to_value_nxfield]
    assert nxroot[path_to_time_nxfield]
    assert isinstance(nxroot[path_to_value_nxfield], NXfield)
    assert isinstance(nxroot[path_to_time_nxfield], NXfield)
    assert_nxobject_and_assonant_data_field_equality(
        nxroot[path_to_value_nxfield], example_int_1d_timeseries_data_field.value
    )
    assert_nxobject_and_assonant_data_field_equality(
        nxroot[path_to_time_nxfield], example_int_1d_timeseries_data_field.timestamps
    )


def test_write_axis_timeseries_within_subcomponent_as_nexus_field(
    nexus_file_writer, base_tmp_dir_path, example_components_collection, example_timeseries_rotation_axis
):
    """
    Validate that AssonantFileWriter correctly save Axis TimeSeries within NeXus file

    PS: Don't need to extensively test data types as that was already tested on previous tests.

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - A group with the same name as the one given to the component must be created within the file
        - A group within the component group must be created with the name as the subcomponent
        - A group within the subcomponent group named 'transformations' must exist
        - A group within the 'transformations' group with the same name as the TimeSeries DataHandler must be created
        - The TimeSeries DataHandler group must be of type NXlog
        - Two nexus fields must exist within the TimeSeries group:
            (1) 'value': nexus field storing value property from the TimeSeries
            (2) 'time': nexus field storing timestamps property from the TimeSeries]
        - The Axis TimeSeries group content must be equivalent to Assonant Axis TimeSeries DataHandler
    """
    filename = "test_nexus"
    component_name = "Monochromator"  # Don't matter which componet is used as subcomponents are the focus
    subcomponent_name = "Mirror"
    timeseries_axis_name = "timeseries_axis"
    component = example_components_collection[component_name]
    subcomponent = example_components_collection[subcomponent_name]
    component_group_name = component_name.lower()
    subcomponent_group_name = subcomponent_name.lower()

    subcomponent.add_position(timeseries_axis_name, example_timeseries_rotation_axis)
    component.add_subcomponent(subcomponent)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    nxroot = nxload(output_file_path, mode="r")

    path_to_axis_group = "/".join(
        [component_group_name, subcomponent_group_name, "transformations", timeseries_axis_name]
    )

    # Check subgroup was created with subcomponent name and with correct Nexus type
    assert nxroot[path_to_axis_group]["value"]
    assert nxroot[path_to_axis_group]["time"]
    assert isinstance(nxroot[path_to_axis_group]["value"], NXfield)
    assert isinstance(nxroot[path_to_axis_group]["time"], NXfield)
    assert_nxobject_and_assonant_axis_equality(nxroot[path_to_axis_group]["value"], example_timeseries_rotation_axis)
    assert_nxobject_and_assonant_data_field_equality(
        nxroot[path_to_axis_group]["time"], example_timeseries_rotation_axis.value.timestamps
    )


def test_write_entries_with_name_conflict_in_nexus(
    nexus_file_writer,
    base_tmp_dir_path,
    example_entry,
    example_int_1d_array_data_field,
    example_float_2d_array_data_field,
):
    """
    Validate that AssonantFileWriter correctly handle writing entries with equal name in the nexus file

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - Due to entry name conflict, a new file must be created to avoid data loss
        - The new file name must be equal to the original name with a index posfix (e.g: 000001)
        - Inside both files, name and content of both entries must be equivalent to its objects data
    """
    filename = "test_nexus"
    entry_name = example_entry.name
    data_field_name = "data_field"

    entry_1 = example_entry.model_copy(deep=True)
    entry_2 = example_entry.model_copy(deep=True)

    entry_1.add_field(data_field_name, example_int_1d_array_data_field)
    entry_2.add_field(data_field_name, example_float_2d_array_data_field)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=entry_1)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=entry_2)

    output_file_1_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    output_file_2_path = Path(base_tmp_dir_path, filename + "_000001").with_suffix(
        nexus_file_writer.get_file_extension()
    )

    # Check file was created
    assert output_file_1_path.exists()
    assert output_file_2_path.exists()

    nxroot_file_1 = nxload(output_file_1_path, mode="r")
    nxroot_file_2 = nxload(output_file_2_path, mode="r")

    # Check nexus content and structure is correct in both files
    assert nxroot_file_1[entry_name]
    assert isinstance(nxroot_file_1[entry_name], NXentry)
    assert nxroot_file_1[entry_name][data_field_name]
    assert isinstance(nxroot_file_1[entry_name][data_field_name], NXfield)
    assert_nxobject_and_assonant_data_field_equality(
        nxroot_file_1[entry_name][data_field_name], example_int_1d_array_data_field
    )

    assert nxroot_file_2[entry_name]
    assert isinstance(nxroot_file_2[entry_name], NXentry)
    assert nxroot_file_2[entry_name][data_field_name]
    assert isinstance(nxroot_file_2[entry_name][data_field_name], NXfield)
    assert_nxobject_and_assonant_data_field_equality(
        nxroot_file_2[entry_name][data_field_name], example_float_2d_array_data_field
    )


def test_write_entries_without_conflict_in_nexus(
    nexus_file_writer, base_tmp_dir_path, example_entry, example_int_1d_array_data_field
):
    """
    Validate that AssonantFileWriter correctly handle writing entries without conflicit name in the nexus file

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - As no name conflict exists between entries, both entries must exist within the same file
        - One NXentry group must exist for each entry with the name given to the entry
        - Both entry content must be equivalent to how it was represented before saved in NeXus
    """
    filename = "test_nexus"
    data_field_name = "data_field"

    entry_1 = example_entry.model_copy(deep=True)
    entry_2 = example_entry.model_copy(deep=True)

    # Differ entry names for test
    entry_1.name = "entry_1_name"
    entry_2.name = "entry_2_name"

    entry_1.add_field(data_field_name, example_int_1d_array_data_field)
    entry_2.add_field(data_field_name, example_int_1d_array_data_field)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=entry_1)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=entry_2)

    output_file_1_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())

    # Check file was created
    assert output_file_1_path.exists()
    nx_root = nxload(output_file_1_path, mode="r")

    # Check nexus content and structure is correct in both files
    assert nx_root[entry_1.name]
    assert isinstance(nx_root[entry_1.name], NXentry)
    assert nx_root[entry_1.name][data_field_name]
    assert isinstance(nx_root[entry_1.name][data_field_name], NXfield)
    assert_nxobject_and_assonant_data_field_equality(
        nx_root[entry_1.name][data_field_name], example_int_1d_array_data_field
    )

    assert nx_root[entry_2.name]
    assert isinstance(nx_root[entry_2.name], NXentry)
    assert nx_root[entry_2.name][data_field_name]
    assert isinstance(nx_root[entry_2.name][data_field_name], NXfield)
    assert_nxobject_and_assonant_data_field_equality(
        nx_root[entry_2.name][data_field_name], example_int_1d_array_data_field
    )


def test_write_entry_with_component_name_conflict_in_nexus(
    nexus_file_writer, base_tmp_dir_path, example_entry, example_components_collection
):
    """
    Validate that AssonantFileWriter correctly handle writing Components with equal name in nexus file

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - Both groups must be store within the same file
        - Due to name conflict, to avoid data loss/overwrite, the second group must be renamed
        - The new name must be the original group name with a posfix index (e.g:' (1)')
        - The content of both groups must be equivalent to how it was before being stored within file
    """
    filename = "test_nexus"
    component_name = "Mirror"
    component_1 = example_components_collection[component_name].model_copy(deep=True)
    component_2 = example_components_collection[component_name].model_copy(deep=True)
    component_group_name = component_name.lower()

    example_entry.beamline.add_subcomponent([component_1, component_2])

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=example_entry)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    nxroot = nxload(output_file_path, mode="r")

    # Check group was created with component name
    assert nxroot[example_entry.name]["instrument"][component_group_name]
    assert nxroot[example_entry.name]["instrument"][component_group_name + " (1)"]


def test_write_component_with_field_name_conflict_in_nexus(
    nexus_file_writer,
    base_tmp_dir_path,
    example_components_collection,
    example_int_1d_array_data_field,
    example_float_2d_array_data_field,
):
    """
    Validate that AssonantFileWriter correctly handle writing fields with equal name in nexus file

    Expected Behavior:
        - AssonantFileWriter must create a new NeXus into target file path with the given file name
        - Both fields must be created within the same Component group
        - Due to name conflict, to avoid data loss/overwrite, the second field must be renamed
        - The new name must be the original field name with a posfix index (e.g:' (1)')
        - The content of both groups must be equivalent to how it was before being stored within file
    """
    filename = "test_nexus"
    component_name = "Mirror"
    field_name = "data_field_name"
    component = example_components_collection[component_name]
    component_group_name = component_name.lower()

    component.add_field(field_name, example_int_1d_array_data_field)
    component.add_field(field_name, example_float_2d_array_data_field)

    nexus_file_writer.write_data(filepath=base_tmp_dir_path, filename=filename, data=component)

    output_file_path = Path(base_tmp_dir_path, filename).with_suffix(nexus_file_writer.get_file_extension())
    nxroot = nxload(output_file_path, mode="r")

    # Check group was created with component name
    assert nxroot[component_group_name][field_name]
    assert nxroot[component_group_name][field_name + " (1)"]

    assert_nxobject_and_assonant_data_field_equality(
        nxroot[component_group_name][field_name], example_int_1d_array_data_field
    )
    assert_nxobject_and_assonant_data_field_equality(
        nxroot[component_group_name][field_name + " (1)"], example_float_2d_array_data_field
    )
