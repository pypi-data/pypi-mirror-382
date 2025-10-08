"""Assonant base data class."""

from pydantic import BaseModel, ConfigDict


# TODO: make this class abstract
class AssonantDataClass(BaseModel):
    """Assonant base data class.

    All Assonant data classes extends this class.
    """

    # Configuration dictionary used by pydantic (v2.0 >)
    model_config = ConfigDict(
        populate_by_name=True,  # Allows to populate with field name when an alias is given
        arbitrary_types_allowed=True,
        extra="forbid",  # https://github.com/pydantic/pydantic/issues/1887
    )
