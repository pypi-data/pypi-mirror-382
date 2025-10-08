"""Tests focused on validating AssonantComponentFactory methods from Data Classes submodule"""

import importlib
import inspect

import pytest

from assonant.data_classes import AssonantComponentFactory
from assonant.data_classes.components import *
from assonant.data_classes.exceptions import AssonantComponentFactoryError


def test_create_component_by_class_name():
    """
    Validate that AssonantComponentFactory correctly instantiates components using their class names.

    Expected Behavior:
        - For every valid class defined in `assonant.data_classes.components`, the factory should:
            - Dynamically resolve the class name.
            - Instantiate the component with the provided name.
            - Return an instance of the expected component class with the correct 'name' attribute.
    """
    for name, cls in inspect.getmembers(importlib.import_module("assonant.data_classes.components"), inspect.isclass):
        component = AssonantComponentFactory.create_component_by_class_name(name, "component_name")
        assert isinstance(component, cls)
        assert component.name == "component_name"


def test_create_component_by_class_name_invalid():
    """
    Validate that AssonantComponentFactory raises an exception for unknown class names.

    Expected Behavior:
        - If the given class name does not exist in the component module,
          the factory should raise an AssonantComponentFactoryError to prevent silent failures.
    """
    with pytest.raises(AssonantComponentFactoryError):
        AssonantComponentFactory.create_component_by_class_name("NonExistentComponent", "bad")


def test_create_component_by_class_type():
    """
    Validate that AssonantComponentFactory correctly instantiates components using their class types.

    Expected Behavior:
        - For every valid component class, the factory should:
            - Accept the class type as input.
            - Instantiate the component using a compatible constructor.
            - Assign the given name to the 'name' attribute.
            - Return a properly typed instance of the component.
    """
    for name, cls in inspect.getmembers(importlib.import_module("assonant.data_classes.components"), inspect.isclass):
        component = AssonantComponentFactory.create_component_by_class_type(cls, "component_name")
        assert isinstance(component, cls)
        assert component.name == "component_name"


def test_create_component_by_class_type_invalid():
    """
    Validate that AssonantComponentFactory raises an error when the class constructor is incompatible.

    Expected Behavior:
        - If the class does not support instantiation with a single `name` argument,
          the factory should detect this and raise an AssonantComponentFactoryError
          to signal improper usage or a misconfigured component class.
    """

    class FakeComponent(Component):
        def __init__(self, fail):
            pass  # wrong signature

    with pytest.raises(AssonantComponentFactoryError):
        AssonantComponentFactory.create_component_by_class_type(FakeComponent, "broken")


def test_create_component_methods_consistency():
    """
    Validate that both AssonantComponentFactory creation methods
    return equal Component instances. That guarantee consistency among creational
    methods.

    Expected Behavior:
        - Both factory methods must return equivalent Component objects.
    """
    for name, cls in inspect.getmembers(importlib.import_module("assonant.data_classes.components"), inspect.isclass):
        component_created_with_class_name = AssonantComponentFactory.create_component_by_class_name(
            name, "component_name"
        )
        component_created_with_class_type = AssonantComponentFactory.create_component_by_class_type(
            cls, "component_name"
        )

        assert component_created_with_class_type == component_created_with_class_name
