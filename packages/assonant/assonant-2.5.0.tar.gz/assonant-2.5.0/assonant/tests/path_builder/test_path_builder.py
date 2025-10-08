"""Tests focused on validating Assonant PathBuilder methods"""

from pathlib import Path

import pytest

from assonant.naming_standards import BeamlineName
from assonant.path_builder import BeamlinePathBuilder


@pytest.fixture(scope="function")
def example_path_builder() -> BeamlinePathBuilder:
    """
    Provides a BeamlinePathBuilder to be used on tests.
    """
    return BeamlinePathBuilder()


@pytest.fixture(scope="session")
def example_proposal_id() -> str:
    """
    Provides a standard example proposal ID to be used on tests.
    """
    return "20250826"


@pytest.fixture(scope="session")
def example_beamline_name() -> str:
    """
    Provides a standard example beamline name to be used on tests.
    """
    return BeamlineName.CARNAUBA.value.lower()


@pytest.fixture(scope="session")
def expected_data_schema_path(example_beamline_name) -> str:
    """
    Provides the expected data schema path considering the example beamline name.
    """
    return str(Path(f"/ibira/lnls/beamlines/{example_beamline_name}/apps/assonant/metadata.csv"))


@pytest.fixture(scope="session")
def expected_proposal_path(example_beamline_name, example_proposal_id) -> str:
    """
    Provides the expected proposal path considering the example beamline name and example proposal id.
    """
    return str(Path(f"/ibira/lnls/beamlines/{example_beamline_name}/proposals/{example_proposal_id}"))


def test_set_beamline_name(example_path_builder, example_beamline_name):
    """
    Validate that BeamlinePathBuilder set_beamline_name method correctly set
    beamline_name property.

    Expected Behavior:
        - BeamlinePathBuilder beamline_name property must have the same value
        than the passed example_beamline_name
    """
    example_path_builder.set_beamline_name(example_beamline_name)
    assert example_path_builder.beamline_name == example_beamline_name


def test_set_proposal_id(example_path_builder, example_proposal_id):
    """
    Validate that BeamlinePathBuilder set_proposal method correctly set
    proposal_id property.

    Expected Behavior:
        - BeamlinePathBuilder proposal_id property must have the same value
        than the passed example_proposal_id
    """
    example_path_builder.set_proposal(example_proposal_id)
    assert example_path_builder.proposal_id == example_proposal_id


def test_build_path_to_data_schema_success(example_path_builder, example_beamline_name, expected_data_schema_path):
    """
    Validate that BeamlinePathBuilder build_path_to_data_schema method
    correctly generate path to beamline data_schema file

    Expected Behavior:
        - BeamlinePathBuilder generated path to data_schema file must
        be the same as the expected data schema path.
    """
    example_path_builder.set_beamline_name(example_beamline_name)
    assert example_path_builder.build_path_to_data_schema() == expected_data_schema_path


def test_build_path_to_data_schema_without_beamline(example_path_builder):
    """
    Validate that BeamlinePathBuilder correctly asserts and raises exception
    if build_path_to_data_schema method is called before setting target
    beamline_name property.

    Expected Behavior:
        - BeamlinePathBuilder must raise an AssertionError signalizing that the
        beamline_name property was not set.
    """
    with pytest.raises(AssertionError, match="Beamline name property must be set"):
        example_path_builder.build_path_to_data_schema()


def test_build_path_to_proposal_success(
    example_path_builder, example_beamline_name, example_proposal_id, expected_proposal_path
):
    """
    Validate that BeamlinePathBuilder build_path_to_proposal method
    correctly generate path to proposal directory

    Expected Behavior:
        - BeamlinePathBuilder generated path to proposal directory file must
        be the same as the expected proposal path.
    """
    example_path_builder.set_beamline_name(example_beamline_name)
    example_path_builder.set_proposal(example_proposal_id)
    assert example_path_builder.build_path_to_proposal() == expected_proposal_path


def test_build_path_to_proposal_without_proposal(example_path_builder, example_beamline_name):
    """
    Validate that BeamlinePathBuilder correctly asserts and raises exception
    if build_path_to_proposal method is called before setting target
    proposal property.

    Expected Behavior:
        - BeamlinePathBuilder must raise an AssertionError signalizing that the
        proposal_id property was not set.
    """

    example_path_builder.set_beamline_name(example_beamline_name)
    with pytest.raises(AssertionError, match="Proposal ID property must be set"):
        example_path_builder.build_path_to_proposal()


def test_build_path_to_proposal_without_beamline(example_path_builder, example_proposal_id):
    """
    Validate that BeamlinePathBuilder correctly asserts and raises exception
    if build_path_to_proposal method is called before setting target
    beamline_name property.

    Expected Behavior:
        - BeamlinePathBuilder must raise an AssertionError signalizing that the
        beamline_name property was not set.
    """

    example_path_builder.set_proposal(example_proposal_id)
    with pytest.raises(AssertionError, match="Beamline name property must be set"):
        example_path_builder.build_path_to_proposal()


def test_reset_functionality(example_path_builder, example_beamline_name, example_proposal_id):
    """
    Validate that BeamlinePathBuilder reset method correctly resets its properties.

    Expected Behavior:
        - BeamlinePathBuilder properties must be reset to None value after
        reset method is called.
    """
    assert example_path_builder.beamline_name is None
    assert example_path_builder.proposal_id is None
    example_path_builder.set_beamline_name(example_beamline_name)
    example_path_builder.set_proposal(example_proposal_id)
    assert example_path_builder.beamline_name is not None
    assert example_path_builder.proposal_id is not None
    example_path_builder.reset()
    assert example_path_builder.beamline_name is None
    assert example_path_builder.proposal_id is None
