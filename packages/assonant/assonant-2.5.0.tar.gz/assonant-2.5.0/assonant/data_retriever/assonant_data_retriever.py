from typing import Any, Dict, List, Union

from assonant.naming_standards import AcquisitionMoment

from .assonant_data_retriever_interface import IAssonantDataRetriever
from .data_retriever_factory import DataRetrieverFactory
from .exceptions.data_retrievers_exceptions import AssonantDataRetrieverError


class AssonantDataRetriever(IAssonantDataRetriever):
    """Assonant Data Retriever.

    Wrapper class that abstracts all process related to creating specific data retrievers
    for specific file formats/ data structures and instatiating components and fields given the retrieved data.
    """

    def __init__(self, data_source: Any):

        # Persist passed data_source
        self.data_source = data_source
        try:
            self.data_retriever = DataRetrieverFactory.create_data_retriever(data_source=data_source)
        except Exception as e:
            raise AssonantDataRetriever(
                f"Failed to create a suitable DataRetriever for data_source of type: {type(data_source)}"
            ) from e

    def get_pv_data_by_acquisition_moment(
        self, acquisition_moment: AcquisitionMoment
    ) -> Dict[str, Union[Any, List[Any]]]:
        """Return collected PV data related to specified AcquisitionMoment.

        The returned value is a dictionary as follow:

        {
            PV_NAME_1: [PV_VALUE_1, PV_VALUE_2, ...],
            PV_NAME_2: PV_VALUE_1,
            ...
        }

        PS: PV values may be a List of values or a single value.

        Args:
            acquisition_moment (AcquisitionMoment): Target Acquisition Moment used to select
            data from which Acquisition Moment will be retrieved.

        Returns:
            Dict[str, Union[Any, List[Any]]]: Dictionary containing retrieved PV data.
        """
        try:
            return self.data_retriever.get_pv_data_by_acquisition_moment(acquisition_moment)
        except Exception as e:
            raise AssonantDataRetrieverError(
                f"Failed to retrieve pv data for '{acquisition_moment.value}' Acquisition Moment"
            ) from e
