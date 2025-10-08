from enum import Enum


class ExperimentStage(Enum):
    """Possible Experiment Stage values."""

    SAMPLE_ACQUISITION = "sample_acquisition"
    SAMPLE_POSITIONING = "sample_positioning"
    FLAT_FIELD_ACQUISITION = "flat_field_acquisition"
    DARK_FIELD_ACQUISITION = "dark_field_acquisition"
    BUFFER_ACQUISITION = "buffer_acquisition"
