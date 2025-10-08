import pytest
from nexusformat.nexus import NXroot

from assonant._nexus import NeXusObjectFactory, NeXusObjectFactoryError
from assonant.data_classes import AssonantDataClass, Entry
from assonant.data_classes.components import Component
from assonant.data_classes.data_handlers import Axis, DataField, TimeSeries

from ..utils import get_component_classes, get_data_handler_classes


@pytest.mark.parametrize("component_cls", get_component_classes())
def test_create_nxobject_matches_component_mapping(component_cls, component_to_nexus_mapping):
    """Test that NeXusObjectFactory creates the correct NXobject for each component."""
    factory = NeXusObjectFactory()
    data_obj: AssonantDataClass = component_cls(name="test_component")

    nxobj = factory.create_nxobject(data_obj)

    # Check expected NeXus class was used for object
    expected_nx_class = component_to_nexus_mapping[component_cls]
    assert isinstance(nxobj, expected_nx_class)


def test_create_nxobject_matches_entry_mapping(example_entry, component_to_nexus_mapping):
    """Test that NeXusObjectFactory creates the correct NXobject for each component."""
    factory = NeXusObjectFactory()

    nxobj = factory.create_nxobject(example_entry)

    # Check expected NeXus class was used for object
    expected_nx_class = component_to_nexus_mapping[Entry]
    assert isinstance(nxobj, expected_nx_class)


@pytest.mark.parametrize("data_handler_cls", get_data_handler_classes())
def test_create_nxobject_matches_data_handler_mapping(
    data_handler_cls,
    data_handler_to_nexus_mapping,
    example_string_data_field,
    example_translation_axis,
    example_int_1d_timeseries_data_field,
    example_timeseries_rotation_axis,
):
    """Test that NeXusObjectFactory creates the correct NXobject for each component."""
    factory = NeXusObjectFactory()

    if data_handler_cls is DataField:
        nxobj = factory.create_nxobject(example_string_data_field)

        expected_nx_class = data_handler_to_nexus_mapping[data_handler_cls]
        assert isinstance(nxobj, expected_nx_class)
    elif data_handler_cls is Axis:
        # Axis is a specific case where it may have an DataField within it or an TimeSeries, depending on it returned
        # nexus object is different
        nxobj = factory.create_nxobject(example_translation_axis)
        nxobj2 = factory.create_nxobject(example_timeseries_rotation_axis)

        expected_nx_classes = data_handler_to_nexus_mapping[data_handler_cls]
        assert type(nxobj) in expected_nx_classes
        assert type(nxobj2) in expected_nx_classes

    elif data_handler_cls is TimeSeries:

        nxobj = factory.create_nxobject(example_int_1d_timeseries_data_field)

        expected_nx_class = data_handler_to_nexus_mapping[data_handler_cls]
        assert isinstance(nxobj, expected_nx_class)
    else:
        raise AssertionError(f"Test for class {data_handler_cls} was not developed!")


def test_create_nxobject_pack_into_nxroot(component_to_nexus_mapping, example_components_collection):
    """Test that objects can be packed into an NXroot when requested."""
    factory = NeXusObjectFactory()
    data_obj = example_components_collection["Detector"]

    nxobj = factory.create_nxobject(data_obj, pack_into_nxroot=True)

    # Check first NeXus class is the NXroot
    assert isinstance(nxobj, NXroot)

    # Check that component NeXus Object was created within NXroot
    assert data_obj.name in nxobj
    assert isinstance(nxobj[data_obj.name], component_to_nexus_mapping[type(data_obj)])


def test_create_nxobject_invalid_component():
    """Test that creating an NXobject from an unsupported component raises an error."""

    class FakeComponent(Component):
        """A dummy component not present in the mapping."""

        pass

    factory = NeXusObjectFactory()
    fake_obj = FakeComponent(name="fake_component")

    with pytest.raises(NeXusObjectFactoryError):
        factory.create_nxobject(fake_obj)
