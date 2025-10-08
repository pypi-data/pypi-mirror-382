"""Assonant Data Classes.

Assonant data classes defines standard grouping classes for acquiring sending,
manipulating and storing data over Assonant modules.

All classes inherits from AssonantDataClass and can be split mainly in 3 types:

1. Components: Data classes responsible to grouping information in logical scopes (e.g: Data from
a detector is stored inside a Detector class, while sample information in a class called Sample)
2. Data Handler: Data classes responsible for standardizing how data is handled inside other
Assonant data classes.
3. Entry: Special class used to group all information related to a specific stage of an
Experiment.

To import and uses data classes from each type, refer to its specific submodule as shown below:

from .assonant_data_class.<sub_module_name> import <data_class_name>, ...
"""

from .assonant_data_class import AssonantDataClass
from .entry import Entry
from .factories import (
    AssonantComponentFactory,
    AssonantDataHandlerFactory,
    AssonantEntryFactory,
)

__all__ = [
    "AssonantComponentFactory",
    "AssonantDataClass",
    "AssonantDataHandlerFactory",
    "AssonantEntryFactory",
    "Entry",
]
