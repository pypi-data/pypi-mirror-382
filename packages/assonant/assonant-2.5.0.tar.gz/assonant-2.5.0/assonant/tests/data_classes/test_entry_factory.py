"""Tests focused on validating Assonant methods from Data Classes submodule"""

import numpy as np
import pytest

from assonant.data_classes import AssonantEntryFactory, Entry
from assonant.data_classes.components import Beamline
from assonant.data_classes.exceptions import AssonantEntryFactoryError
from assonant.naming_standards import BeamlineName

# ================== Utilitary methods ==================


def assert_entry(entry: Entry, input_entry_name: str, input_beamline_name: BeamlineName):
    """Assert that Entry was correctly created based on input values

    Args:
        entry (Entry): Entry which assertion will be applied over.
        input_entry_name (str): Input entry_name parameter during Entry creation.
        input_beamline_name (BeamlineName): Input beamline_name parameter during Entry creation.

    Raise:
        AssertionError: Raises if any assertion fails.
    """
    assert isinstance(entry, Entry)
    assert entry.name == input_entry_name
    assert isinstance(entry.beamline, Beamline)
    assert entry.beamline.name == input_beamline_name.value


invalid_entry_names = [10, None, [1, 2, 3, 4], np.array([1, 2, 3, 4])]
invalid_beamline_names = ["name", 10, None, [1, 2, 3, 4], np.array([1, 2, 3, 4])]

# ================== Tests ==================


@pytest.mark.parametrize("entry_name, beamline_name", [("entry", bealine_name) for bealine_name in BeamlineName])
def test_entry_creation(entry_name, beamline_name):
    """
    Validate that AssonantEntryFactory correctly creates entries for all valid beamline names.

    Expected Behavior:
        - Given a valid `entry_name` and a valid `beamline_name` (from BeamlineName enum),
          the factory should:
            - Successfully instantiate an Assonant Entry object.
            - Set the entry's name and beamline attributes accordingly.
        - The resulting entry should pass all structural and semantic validations via `assert_entry`.
    """
    entry = AssonantEntryFactory.create_entry(entry_name=entry_name, beamline_name=beamline_name)

    assert_entry(entry, entry_name, beamline_name)


@pytest.mark.parametrize("entry_name", invalid_entry_names)
def test_entry_creation_invalid_name_type(entry_name):
    """
    Ensure that AssonantEntryFactory raises an error when provided with an invalid entry name.

    Expected Behavior:
        - For each invalid `entry_name` (e.g., non-string types, empty values),
          the factory should:
            - Raise an AssonantEntryFactoryError.
            - Not return an AssonantEntry instance.
        - This safeguards against improper usage and maintains entry name integrity.
    """
    with pytest.raises(AssonantEntryFactoryError):
        _ = AssonantEntryFactory.create_entry(entry_name=entry_name, beamline_name=BeamlineName.CARNAUBA)


@pytest.mark.parametrize("beamline_name", invalid_beamline_names)
def test_entry_creation_invalid_beamline_name_type(beamline_name):
    """
    Ensure that AssonantEntryFactory raises an error when provided with an invalid beamline name.

    Expected Behavior:
        - For each invalid `beamline_name` (Any values different from Assonant BeamlineName enum),
          the factory should:
            - Raise an AssonantEntryFactoryError.
            - Not return an AssonantEntry instance.
        - This safeguards against improper usage and maintains entry name integrity.
    """
    with pytest.raises(AssonantEntryFactoryError):
        _ = AssonantEntryFactory.create_entry(entry_name="entry", beamline_name=beamline_name)
