from enum import Enum


class ValuePlaceholders(Enum):
    """Placeholder values to identify acquisition status or failure."""

    PV_NOT_CONNECTED = "PV not Connected"  # Used when PV was disconnected during acquisition tentative
    VALUE_NOT_SET = "Value not set"  # Used as placeholder value when a value was not set to a field yet
