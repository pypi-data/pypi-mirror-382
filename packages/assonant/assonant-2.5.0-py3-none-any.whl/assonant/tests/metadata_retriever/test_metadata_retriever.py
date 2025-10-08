"""Tests focused on validating AssonantMetadataRetriever methods"""

import pytest

from assonant.metadata_retriever import AssonantMetadataRetriever
from assonant.metadata_retriever.enums import CSVColumn
from assonant.metadata_retriever.exceptions import MetadataRetrieverFactoryError

from ..utils import assert_structure_has_keys

# NOTE: Most of tests (if not all) are not validating returned content as
# CSVMetadataRetriever currently alter value formatting. That said just
# returned structure is being asserted on those tests. If a refactor of
# the CSVMetadataRetriever and AssonantMetadataRetriever occur, checking
# returned content may make sense.

# Define mandatory and optinal fields dict for get_component_info() method returned dict
GET_COMPONENT_INFO_MANDATORY_COMPONENT_KEYS = {"name", "class"}
GET_COMPONENT_INFO_OPTIONAL_COMPONENT_KEYS = {"subcomponent_of"}

# Define mandatory and optinal fields dict for get_pvs_info() method returned dict
GET_PV_INFO_MANDATORY_COMPONENT_KEYS = {"name", "class"}
GET_PV_INFO_OPTIONAL_COMPONENT_KEYS = {"subcomponent_of"}
GET_PV_INFO_MANDATORY_HANDLER_KEYS = {"name", "value", "pv_name"}
GET_PV_INFO_OPTIONAL_HANDLER_KEYS = {"unit", "transformation_type"}


@pytest.fixture(scope="session")
def example_csv_metadata_retriever(example_csv_metadata_file_path) -> AssonantMetadataRetriever:
    """
    Provides a functional AssonantMetadataRetriever for the example_metadata.csv.
    """
    return AssonantMetadataRetriever(metadata_source_file_path=example_csv_metadata_file_path)


def test_invalid_file_format():
    """
    Validate that AssonantMetadataRetriever constructor correctly raises exception
    if path to a file of an unsupported file format is passed during object construction.

    Expected Behavior:
        - AssonantMetadataRetriever must raise an MetadataRetrieverFactoryError if an filepath for unsupported
        file format is passed.
    """
    with pytest.raises(MetadataRetrieverFactoryError):
        _ = AssonantMetadataRetriever(metadata_source_file_path="UNSUPPORTED_FILE_FORMAT")


def test_get_component_info_returned_structure_for_existing_component(example_csv_metadata_retriever):
    """
    Validate that AssonantMetadataRetriever get_component_info() method correctly return expected
    value when component does exist.

    Expected Behavior:
        - AssonantMetadataRetriever be able to return a dictionary containing retrieved metadata
        from the component
        - The dictionary structure must follow exactly the one define at the
        IAssonantMetadataRetriever interface.
    """
    component_name = "ATTENUATOR"
    retrieved_metadata = example_csv_metadata_retriever.get_component_info(component_name)

    comp_info = retrieved_metadata["component_info"]
    assert_structure_has_keys(
        comp_info, GET_COMPONENT_INFO_MANDATORY_COMPONENT_KEYS, GET_COMPONENT_INFO_OPTIONAL_COMPONENT_KEYS
    )


def test_get_component_info_returned_structure_for_existing_subcomponent(example_csv_metadata_retriever):
    """
    Validate that AssonantMetadataRetriever get_component_info() method correctly return expected
    value when component does exist and is a subcomponent.

    Expected Behavior:
        - AssonantMetadataRetriever be able to return a dictionary containing retrieved metadata
        from the component
        - The dictionary structure must follow exactly the one define at the
        IAssonantMetadataRetriever interface.
        - The dictionary structure must contain the  subcomponent_of field
    """
    component_name = "SUBCOMP_SENSOR"
    retrieved_metadata = example_csv_metadata_retriever.get_component_info(component_name)

    comp_info = retrieved_metadata["component_info"]
    assert_structure_has_keys(
        comp_info, GET_COMPONENT_INFO_MANDATORY_COMPONENT_KEYS, GET_COMPONENT_INFO_OPTIONAL_COMPONENT_KEYS
    )


def test_get_component_info_for_non_existing_component(example_csv_metadata_retriever):
    """
    Validate that AssonantMetadataRetriever get_component_info() method correctly
    return expected value when component does not exist.

    Expected Behavior:
        - AssonantMetadataRetriever must not break or raise an exception in this case
        - The returned value must be None
    """
    retrived_metadata = example_csv_metadata_retriever.get_component_info("this component name does not exist")
    assert retrived_metadata == {}


def test_get_subcomponents_mapping(example_csv_metadata_retriever, example_metadata_csv_df):
    """
    Validate that AssonantMetadataRetriever get_subcomponents_mapping() method correctly
    retrieves a mapping of components that contains subcomponents.

    Expected Behavior:
        - AssonantMetadataRetriever must return the information in the expected structure defined
        in the IAssonantMetadataRetriever Interface
        - The dictionary structure must contain the correct number of components that contains subcomponents
        - component and subcomponents names must be correct
    """
    n_of_components_with_subcomponents = example_metadata_csv_df[CSVColumn.SUBCOMPONENT_OF.value].nunique(dropna=True)
    n_of_subcomponents = sum(example_metadata_csv_df[CSVColumn.SUBCOMPONENT_OF.value].value_counts(dropna=True))

    mapping = example_csv_metadata_retriever.get_subcomponents_mapping()

    assert len(mapping.keys()) == n_of_components_with_subcomponents
    assert n_of_subcomponents == sum([len(v) for v in mapping.values()])


def test_get_single_pv_info_return_mandatory_structure(example_csv_metadata_retriever):
    """
    Validate that AssonantMetadataRetriever get_pvs_info() method correctly
    retrieves info related to a PV when a single PV name is passed.

    Expected Behavior:
        - AssonantMetadataRetriever must return the information in the expected structure defined
        in the IAssonantMetadataRetriever Interface.
    """
    pv_name = "ATTENUATOR_PV"
    pv_info = example_csv_metadata_retriever.get_pvs_info(pv_name)

    assert pv_info[pv_name]

    comp_info = pv_info[pv_name]["component_info"]
    handler_info = pv_info[pv_name]["data_handler_info"]

    # Enforce contract
    assert_structure_has_keys(comp_info, GET_PV_INFO_MANDATORY_COMPONENT_KEYS, GET_PV_INFO_OPTIONAL_COMPONENT_KEYS)
    assert_structure_has_keys(handler_info, GET_PV_INFO_MANDATORY_HANDLER_KEYS, GET_PV_INFO_OPTIONAL_HANDLER_KEYS)


def test_get_multiple_pv_info(example_csv_metadata_retriever):
    """
    Validate that AssonantMetadataRetriever get_pvs_info() method correctly
    retrieves info related to when multiple PV names are passed as input.

    Expected Behavior:
        - AssonantMetadataRetriever must return the information in the expected structure defined
        in the IAssonantMetadataRetriever Interface.
    """
    pv_names = ["ATTENUATOR_PV", "SENSOR_PV"]
    pvs_info = example_csv_metadata_retriever.get_pvs_info(pv_names)

    assert all(pv_name in pvs_info.keys() for pv_name in pv_names)

    for pv_name in pv_names:
        comp_info = pvs_info[pv_name]["component_info"]
        handler_info = pvs_info[pv_name]["data_handler_info"]

        # Enforce contract
        assert_structure_has_keys(comp_info, GET_PV_INFO_MANDATORY_COMPONENT_KEYS, GET_PV_INFO_OPTIONAL_COMPONENT_KEYS)
        assert_structure_has_keys(handler_info, GET_PV_INFO_MANDATORY_HANDLER_KEYS, GET_PV_INFO_OPTIONAL_HANDLER_KEYS)


def test_get_unexisting_pv_info(example_csv_metadata_retriever):
    """
    Validate that AssonantMetadataRetriever get_pvs_info() method correctly
    retrieves info related to a PV when an single PV name is passed.

    Expected Behavior:
        - AssonantMetadataRetriever must return the information in the expected structure defined
        in the IAssonantMetadataRetriever Interface.
    """
    pv_name = "This pv does not exist"
    pv_info = example_csv_metadata_retriever.get_pvs_info(pv_name)
    assert pv_info == {}
