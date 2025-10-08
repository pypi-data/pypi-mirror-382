"""Assonant Detector component data class."""

from .component import Component


class Detector(Component):
    """Data class to handle all data required to define a detector."""


class DetectorModule(Component):
    """Data class to handle all data required to define a Module from a Detector."""


class DetectorROI(Component):
    """Data class to handle all data required to define a Region of Interest(ROI) taken from a Detector."""


class DetectorChannel(Component):
    """Data class to handle all data required to define a Channel from a Detector."""
