from enum import Enum


class ValuePlaceholders(Enum):
    """Placeholder values to identify acquisition status or failure."""

    PV_NOT_CONNECTED = "PV not Connected"
    VALUE_NOT_SET = "Value not set"
