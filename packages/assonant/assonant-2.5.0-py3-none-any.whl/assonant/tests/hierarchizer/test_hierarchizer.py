"""Tests focused on validating Hierarchizer methods"""

from unittest.mock import MagicMock

import pytest

from assonant.hierarchizer import Hierarchizer
from assonant.hierarchizer.exceptions import AssonantHierarchizerError


@pytest.fixture
def mock_metadata_retriever() -> MagicMock:
    """Fixture that returns a mocked AssonantMetadataRetriever."""
    mock = MagicMock()
    return mock


def test_init_with_custom_metadata_retriever(mock_metadata_retriever):
    """Ensure constructor uses provided metadata retriever instead of creating a new one.

    Expected Behavior:
        - Hierarchizer internal metadata_retriever must be equal to the one passed
        in its constructor method
    """
    hier = Hierarchizer("fake_schema.csv", metadata_retriever=mock_metadata_retriever)
    assert hier.metadata_retriever is mock_metadata_retriever


def test_init_with_invalid_schema_path_raises():
    """Ensure exception is wrapped in AssonantHierarchizerError if retriever fails.

    Expected Behavior:
        - Hierarchizer must raise and AssonantHierarchizerError to signalize invalid schema
    """
    with pytest.raises(AssonantHierarchizerError):
        Hierarchizer("invalid_schema.csv")


def test_mount_tree_node_set_root(mock_metadata_retriever):
    """Ensure mount_tree_node_set method correctly mount set for root Component (Component
    without parent).

    Expected Behavior:
        - If a component has no parent, it should return a set with only its tuple
    """
    hier = Hierarchizer("schema.csv", metadata_retriever=mock_metadata_retriever)
    root_tuple = ("root", "Beamline", None)
    result = hier._mount_tree_node_set(root_tuple)
    assert result == {root_tuple}


def test_mount_tree_node_set_with_parent(mock_metadata_retriever):
    """Ensure mount_tree_node_set method correctly mount set when component there are
    components with parent components.

    Expected Behavior:
        - If a component has a parent, the returned set must contain it and also its
        parent. This behavior must eb recursive until gets to a root Component
    """
    hier = Hierarchizer("schema.csv", metadata_retriever=mock_metadata_retriever)

    parent_info = {"component_info": {"name": "root", "class": "Beamline"}}
    mock_metadata_retriever.get_component_info.return_value = parent_info

    child_tuple = ("child", "Mirror", "root")
    result = hier._mount_tree_node_set(child_tuple)

    assert result == {("child", "Mirror", "root"), ("root", "Beamline", None)}


def test_hierarchize_components_with_entry_and_beamline(mock_metadata_retriever, example_entry):
    """Ensure hierarchize_components method correctly handle special case of Entry
    and Beamline Components.

    Expected Behavior:
        - Entry and Beamline should remain unchanged and returned as-is.
    """
    hier = Hierarchizer("schema.csv", metadata_retriever=mock_metadata_retriever)

    components = [example_entry, example_entry.beamline]
    result = hier.hierarchize_components(components)

    # Should return unchanged
    assert result == components


def test_hierarchize_components_without_hierarchy(mock_metadata_retriever, example_components_collection):
    """Ensure hierarchy is built correctly for list of components without parent (root components).

    Expected Behavior:
        - The list returned by the hierarchizer must be equal to the input list.
    """
    hier = Hierarchizer("schema.csv", metadata_retriever=mock_metadata_retriever)

    monoch = example_components_collection["Monochromator"]
    mirror = example_components_collection["Mirror"]
    input_monoch = example_components_collection["Monochromator"].model_copy(deep=True)
    input_mirror = example_components_collection["Mirror"].model_copy(deep=True)

    # This is the expected result
    monoch.add_subcomponent(mirror)

    # Mock Metadata retriever to return that mirror is subcomponent of monochromator
    def get_info(name):
        """MetadataRetriever.get_component_info method mock"""
        if name == monoch.name:
            return {"component_info": {"name": "monochromator", "class": "Monochromator"}}
        elif name == mirror.name:
            return {"component_info": {"name": "mirror", "class": "Mirror"}}

    mock_metadata_retriever.get_component_info.side_effect = get_info

    components = [input_monoch, input_mirror]
    result = hier.hierarchize_components(components)

    # Iterate over result to compare lists. As order the same order is not guaranteed and Components are
    # not hashable to be converted to a set or sortable, manually compare if elements from a list
    # is within the other
    assert all(component in result for component in components)


def test_hierarchize_components_with_simple_hierarchy(mock_metadata_retriever, example_components_collection):
    """Ensure hierarchy is built correctly for components with parent-child relation.

    Expected Behavior:
        - The list returned by the hierarchizer must be different from input list.
        - Child components must be within its parent component subcomponents group
        - Returned list must contain only root Components (non-parent Components)
    """
    hier = Hierarchizer("schema.csv", metadata_retriever=mock_metadata_retriever)

    monoch = example_components_collection["Monochromator"]
    mirror = example_components_collection["Mirror"]
    input_monoch = example_components_collection["Monochromator"].model_copy(deep=True)
    input_mirror = example_components_collection["Mirror"].model_copy(deep=True)

    # This is the expected result
    monoch.add_subcomponent(mirror)

    # Mock Metadata retriever to return that mirror is subcomponent of monochromator
    def get_info(name):
        """MetadataRetriever.get_component_info method mock"""
        if name == monoch.name:
            return {"component_info": {"name": "monochromator", "class": "Monochromator"}}
        elif name == mirror.name:
            return {"component_info": {"name": "mirror", "class": "Mirror", "subcomponent_of": "monochromator"}}

    mock_metadata_retriever.get_component_info.side_effect = get_info

    components = [input_monoch, input_mirror]
    result = hier.hierarchize_components(components)

    assert result != components
    assert len(result) == 1
    assert result[0] == monoch


def test_hierarchize_components_with_multi_subcomponent_hierarchy(
    mock_metadata_retriever, example_components_collection
):
    """Ensure hierarchy is built correctly for components with many parent-child relation.

    Expected Behavior:
        - The list returned by the hierarchizer must be different from input list.
        - Child components must be within its parent component subcomponents group
        - Returned list must contain only root Components (non-parent Components) with its children
        components within it
    """
    hier = Hierarchizer("schema.csv", metadata_retriever=mock_metadata_retriever)

    monoch = example_components_collection["Monochromator"]
    mirror = example_components_collection["Mirror"]
    detector = example_components_collection["Detector"]
    attenuator = example_components_collection["Attenuator"]

    input_monoch = example_components_collection["Monochromator"].model_copy(deep=True)
    input_mirror = example_components_collection["Mirror"].model_copy(deep=True)
    input_detector = example_components_collection["Detector"].model_copy(deep=True)
    input_attenuator = example_components_collection["Attenuator"].model_copy(deep=True)

    # This is the expected result
    monoch.add_subcomponent(mirror)
    attenuator.add_subcomponent(detector)
    monoch.add_subcomponent(attenuator)

    # Mock Metadata retriever to return that mirror is subcomponent of monochromator
    def get_info(name):
        """MetadataRetriever.get_component_info method mock"""
        if name == monoch.name:
            return {"component_info": {"name": "monochromator", "class": "Monochromator"}}
        elif name == mirror.name:
            return {"component_info": {"name": "mirror", "class": "Mirror", "subcomponent_of": "monochromator"}}
        elif name == attenuator.name:
            return {"component_info": {"name": "attenuator", "class": "Attenuator", "subcomponent_of": "monochromator"}}
        elif name == detector.name:
            return {"component_info": {"name": "detector", "class": "Detector", "subcomponent_of": "attenuator"}}

    mock_metadata_retriever.get_component_info.side_effect = get_info

    components = [input_monoch, input_mirror, input_detector, input_attenuator]
    result = hier.hierarchize_components(components)

    assert result != components
    assert len(result) == 1
    assert result[0] == monoch


def test_hierarchize_components_creates_missing_components_in_hierarchy(
    mock_metadata_retriever, example_components_collection
):
    """Ensure hierarchy is built correctly when a child component is passed but its
    parent component is not in the input list.

    Expected Behavior:
        - The list returned by the hierarchizer must be different from input list.
        - The Child components must be within its respective parent component
        internal subcomponents group
        - The Non-passed parent Component must be created internally by hierarchizer, even
        if it is a root Component.
        - Returned list must contain only root Component (non-parent Components) with
        its children component within it
    """
    hier = Hierarchizer("schema.csv", metadata_retriever=mock_metadata_retriever)

    monoch = example_components_collection["Monochromator"]
    mirror = example_components_collection["Mirror"]
    input_mirror = example_components_collection["Mirror"].model_copy(deep=True)

    # This is the expected result
    monoch.add_subcomponent(mirror)

    # Mock Metadata retriever to return that mirror is subcomponent of monochromator
    def get_info(name):
        """MetadataRetriever.get_component_info method mock"""
        if name == monoch.name:
            return {"component_info": {"name": "monochromator", "class": "Monochromator"}}
        elif name == mirror.name:
            return {"component_info": {"name": "mirror", "class": "Mirror", "subcomponent_of": "monochromator"}}

    mock_metadata_retriever.get_component_info.side_effect = get_info

    # Only pass the subcomponent as input to validated that hierarchizer creates parent component
    components = [input_mirror]
    result = hier.hierarchize_components(components)

    assert result != components
    assert len(result) == 1
    assert result[0] == monoch


def test_hierarchize_components_with_multi_missing_subcomponent_hierarchy(
    mock_metadata_retriever, example_components_collection
):
    """Ensure hierarchy is built correctly when many child components are passed but their
    parent components are not in the input list.

    Expected Behavior:
        - The list returned by the hierarchizer must be different from input list.
        - All Child components must be within their respective parent component
        internal subcomponents group
        - All Non-passed parent Components must be created internally by hierarchizer, even
        if it is a root Component.
        - Returned list must contain only root Component (non-parent Components) with
        its children components within it
    """
    hier = Hierarchizer("schema.csv", metadata_retriever=mock_metadata_retriever)

    monoch = example_components_collection["Monochromator"]
    mirror = example_components_collection["Mirror"]
    detector = example_components_collection["Detector"]
    attenuator = example_components_collection["Attenuator"]

    input_mirror = example_components_collection["Mirror"].model_copy(deep=True)
    input_detector = example_components_collection["Detector"].model_copy(deep=True)

    # This is the expected result
    monoch.add_subcomponent(mirror)
    attenuator.add_subcomponent(detector)
    monoch.add_subcomponent(attenuator)

    # Mock Metadata retriever to return that mirror is subcomponent of monochromator
    def get_info(name):
        """MetadataRetriever.get_component_info method mock"""
        if name == monoch.name:
            return {"component_info": {"name": "monochromator", "class": "Monochromator"}}
        elif name == mirror.name:
            return {"component_info": {"name": "mirror", "class": "Mirror", "subcomponent_of": "monochromator"}}
        elif name == attenuator.name:
            return {"component_info": {"name": "attenuator", "class": "Attenuator", "subcomponent_of": "monochromator"}}
        elif name == detector.name:
            return {"component_info": {"name": "detector", "class": "Detector", "subcomponent_of": "attenuator"}}

    mock_metadata_retriever.get_component_info.side_effect = get_info

    components = [input_mirror, input_detector]
    result = hier.hierarchize_components(components)

    assert result != components
    assert len(result) == 1
    assert result[0] == monoch
