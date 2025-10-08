from enum import Enum


class CSVColumn(Enum):
    """CSV column values."""

    NAME = "Name"
    SUBCOMPONENT_OF = "Subcomponent of"
    CLASS = "Class"
    FIELD_NAME = "Field Name"
    UNIT_OF_MEASUREMENT = "Unit of Measurement"
    DATA_TYPE = "Data Type"
    ACQUISITION_TYPE = "Acquisition Type"
    PV_NAME = "PV Name"
    NEXUS_CLASS = "NeXus Class"
    NEXUS_FIELD_NAME = "NeXus Field Name"
    TRANSFORMATION_TYPE = "Transformation Type"
