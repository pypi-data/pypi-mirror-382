from enum import Enum


class AcquisitionType(Enum):
    """Possible Acquisition Types values."""

    SNAPSHOT = "Snapshoted at Exp. Start/end"
    SCAN = "Scanned During Exp."
    VARY = "Vary Among Exps."
