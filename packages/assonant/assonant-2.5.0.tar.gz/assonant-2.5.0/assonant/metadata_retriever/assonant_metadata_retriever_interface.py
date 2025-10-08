from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

from assonant.naming_standards import AcquisitionMoment


class IAssonantMetadataRetriever(ABC):
    """Assonant Metadata Retriever Interface.

    This interface defines what must be implemented by a class to be a Metadata Retriever
    in Assonant environment.
    """

    @abstractmethod
    def get_pv_names_by_acquisition_moment(self, acquisition_moment: AcquisitionMoment) -> List[str]:
        """Return a List with all PV names related to the passed AcquisitionMoment.

        Returned Structure Definition:
        [
            PV_1_NAME,
            PV_2_NAME,
            PV_3_NAME,
            ...
            PV_N_NAME
        ]

        Args:
            acquisition_moment (AcquisitionMoment): Target Acquisition Moment used for selecting which
            PV names will be returned.

        Raises:
            AssonantMetadataRetrieverError: Failure to retrieve requested metadata.

        Returns:
            List[str]: List containing all PV names related to passed AcquisitionMoment.
        """

    @abstractmethod
    def get_pvs_info(self, pv_names: Union[str, List[str]]) -> Dict[str, Dict[str, Any]]:
        """Return all information about the PV paired by the its name.

        Example of return structure.:
        {
            PV_1_NAME_: {
                component_info:
                {
                    name: COMPONENT_NAME,
                    class: COMPONENT_CLASS,
                    subcomponent_of: ASCENDANT_COMPONENT_NAME (if exists)
                },
                data_handler_info:
                {
                    name: FIELD_NAME,
                    value: PLACEHOLDER_VALUE,
                    pv_name: PV_1_NAME,
                    unit: FIELD_UNIT (if exists),
                    transformation_type: FIELD_TRANSFORMATION_TYPE (if exists),
                    PV_1_EXTRA_METADATA_1_NAME: PV_1_EXTRA_METADATA_1_VALUE (if exists),
                    PV_1_EXTRA_METADATA_2_NAME: PV_1_EXTRA_METADATA_2_VALUE (if exists),
                    ...
                }
            },
            PV_2_NAME_: {
                component_info:
                {
                    name: COMPONENT_NAME,
                    class: COMPONENT_CLASS,
                    subcomponent_of: ASCENDANT_COMPONENT_NAME (if exists),
                },
                data_handler_info:
                {
                    name: FIELD_NAME,
                    value: PLACEHOLDER_VALUE,
                    pv_name: PV_2_NAME,
                    unit: FIELD_UNIT (if exists),
                    transformation_type: FIELD_TRANSFORMATION_TYPE (if exists),
                    PV_2_EXTRA_METADATA_1_NAME: PV_2_EXTRA_METADATA_1_VALUE (if exists),
                    PV_2_EXTRA_METADATA_2_NAME: PV_2_EXTRA_METADATA_2_VALUE (if exists),
                    ...
                }
            },
        }

        Args:
            pv_names (List[str]): List with PV names which metadata info will be fetched.

        Raises:
            AssonantMetadataRetrieverError: Failure to retrieve requested metadata.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary containing all PV info paired by the PV name.
        """

    @abstractmethod
    def get_subcomponents_mapping(self) -> Dict[str, List[str]]:
        """Return a Dictionary mapping component names with the name of its subcomponents.

        This call MUST be indepedent of the AcquisitionMoment as components hierarchy is not related to
        acquisition directly but logical organization. If AcquisitionMoment is considered here, it may
        generate hierarchy inconsistency due to the possibility of parent Component exist in some
        AcquisitionMoments and not in others.

        Important considerations about the returned structure:
            * The returned structure contains only Components that have at least one Subcomponent.
            * Subcomponent can contain Subcomponents, that said, names that appears as Subcomponents
            for a Component may also appear as Component with other Subcomponents. Treating how to
            deal with this is responsibility of who is calling this method.

        Example of returned structure:
        {
            COMPONENT_1_NAME: [SUBCOMPONENT_1_NAME, SUBCOMPONENT_2_NAME, ...],
            COMPONENT_2_NAME: [SUBCOMPONENT_1_NAME, SUBCOMPONENT_2_NAME, ...],
            ...
        }

        Raises:
            AssonantMetadataRetrieverError: Failure to retrieve requested metadata.

        Returns:
            Dict[str, List[str]]: Dictionary mapping the name of each Component that contains at
            least one Subcomponent with their respective List of Subcomponents names.
        """

    @abstractmethod
    def get_component_info(self, component_name: str) -> Dict[str, Dict[str, Any]]:
        """Retrieve info about a specific Component based on passed component_name.

        Example of returned structure:
            CHECK get_pvs_info() 'component_info' structure. IT MUST BE THE SAME.

        Args:
            component_name (str): Component name to retrieve information about.

        Raises:
            AssonantMetadataRetrieverError: Failure to retrieve requested data.

        Returns:
            Dict[str, Dict[str, Any]]: Component info dictionary following the same subdictionary
            returned by get_pvs_info() method to represent component info.
        """
