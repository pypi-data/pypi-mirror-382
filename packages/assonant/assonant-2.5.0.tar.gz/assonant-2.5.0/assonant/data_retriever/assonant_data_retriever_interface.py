from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

from assonant.naming_standards import AcquisitionMoment


class IAssonantDataRetriever(ABC):
    """Assonant Data Retriever Interface.

    This interface defines what must be implemented by a class to be a Data Retriever
    in Assonant environment.
    """

    @abstractmethod
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
