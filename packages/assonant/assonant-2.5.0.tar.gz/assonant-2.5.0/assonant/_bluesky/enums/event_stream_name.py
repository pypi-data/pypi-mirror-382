from enum import Enum


class EventStreamName(Enum):
    """Possible Event Streams names from Bluesky."""

    PRIMARY = "primary"
    MONITOR = "monitor"
    BASELINE = "baseline"
