"""Assonant event base abstract class."""

from pydantic import BaseModel, ConfigDict


# TODO: make this class abstract
class AssonantEvent(BaseModel):
    """Assonant base event class.

    All Assonant event classes extends this class.
    """

    # Configuration dictionary used by pydantic (v2.0 >)
    model_config = ConfigDict(
        populate_by_name=True,  # Allows to populate with field name when an alias is given
        arbitrary_types_allowed=True,
        extra="forbid",  # https://github.com/pydantic/pydantic/issues/1887
    )
