"""Assonant Experiment Done Event class."""

from .assonant_event import AssonantEvent


class ExperimentDone(AssonantEvent):
    """Event class to signalize that a experiment has finished.

    This event class gather data required to signalize that a experiment has finished and also
    that allow accessing the data generated during the experiment.
    """

    beamline: str
    filepath: str
