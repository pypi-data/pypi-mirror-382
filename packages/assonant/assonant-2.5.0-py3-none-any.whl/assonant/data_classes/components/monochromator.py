"""Assonant Monochromator component data class."""

from .component import Component


class Monochromator(Component):
    """Data class to handle all data required to define a monochromator."""


class MonochromatorCrystal(Component):
    """Data class to handle all data required to define a crystal from a Monochromator."""


class MonochromatorVelocitySelector(Component):
    """Data class to handle all data required to define a Velocity Selector from a Monochromator."""
