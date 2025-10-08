"""Assonant Sensor component data class."""

from .component import Component


class Sensor(Component):
    """Data class to handle all data required to define a sensor.

    Sensors are Sensors are considered devices that acquired somekind
    of measurement related to the environment or device/sample
    condition (e.g: Photodiode, vacuum pump, thermometer, etc).
    """
