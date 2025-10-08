from enum import Enum


class AcquisitionMoment(Enum):
    """Possible Acquisition Moment values."""

    START = "start"
    DURING = "during"
    END = "end"
