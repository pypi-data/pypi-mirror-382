"""Assonant Path Builder.

Assonant Path builder submodule defines Builders classes responsible to
centralize and standardize path mounting tasks inside Assonant. With this
submodule, different classes to handle specific directories structures
within or outside Sirius can be handled by those classes and made easy to
maintain. 

The idea is to follow the Builder Design pattern within the classes in this
submodule.

Reference: https://refactoring.guru/design-patterns/builder
"""

from .beamline_path_builder import BeamlinePathBuilder

__all__ = ["BeamlinePathBuilder"]
