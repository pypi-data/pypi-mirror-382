"""Assonant data classes - Events submodule.

Event classes responsible for standardizing how specific signalizations are done
in Assonant.
"""

from .assonant_event import AssonantEvent
from .experiment_done import ExperimentDone

__all__ = ["AssonantEvent", "ExperimentDone"]
