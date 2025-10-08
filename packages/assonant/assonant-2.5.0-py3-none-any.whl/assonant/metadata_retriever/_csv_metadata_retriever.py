from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd

from assonant.data_classes.enums import ValuePlaceholders
from assonant.naming_standards import AcquisitionMoment

from .assonant_metadata_retriever_interface import IAssonantMetadataRetriever
from .enums import AcquisitionType, CSVColumn
from .exceptions import AssonantMetadataRetrieverError

# NOTE: Futurally, may be interesting to refactor this class. It is changing the original value
# from how it is represented in the CSV during the pre-processing. If there will be a standardization
# on formatting of some fields (e.g: name is always lower case) may be it should be done in the
# AssonantMetadataRetriever layer or in the application layer and not in the format specific layer.
# BEFORE DOING THIS REFACTOR, CHECK IF THIS MESSAGE IS NOT DEPRECATED.


class CSVMetadataRetriever(IAssonantMetadataRetriever):
    """CSV Metadata Retriever."""

    def __init__(self, csv_file_path: str):

        self.invalid_values = [None, np.nan, ""]

        self.df = pd.read_csv(csv_file_path, sep=",", header=1)

        self._clean_data()

        self._pre_process()

    def _clean_data(self):
        """Apply data cleaning steps over dataframe. This methods should focus on steps which will make some
        kind of row/column removal/drop for some reason (e.g: Rows with not accept values).

        Raises:
            AssonantMetadataRetrieverError: Raised when a problem occurs in any of the data cleaning steps
        """
        try:
            # Remove all without defined class!
            self.df = self.df[self.df[CSVColumn.CLASS.value].notna()]
            # Remove all rows related to Experiment. Temporary limitation for tests!
            self.df = self.df[self.df[CSVColumn.CLASS.value] != "Experiment"]
            self.df = self.df[self.df[CSVColumn.CLASS.value] != "Aperture"]
            self.df = self.df[self.df[CSVColumn.CLASS.value] != "Valve"]
        except Exception as e:
            raise AssonantMetadataRetrieverError(
                "[CLEAN-METADATA] CSV metadata retriever failed while filtering columns!"
            ) from e
        # pass # No data cleaning currently needed

    def _pre_process(self):
        """Apply pre-processing steps over dataframe. This methods should focus on steps which will make some kind
        of transformation over metadata from the Dataframe (e.g: Transform field values into str type).

        Raises:
            AssonantMetadataRetrieverError: Raised when a problem occurs in any of the pre-processing steps
        """
        try:
            # Replace np.nan value to None
            self.df = self.df.replace(np.nan, None)
        except Exception as e:
            raise AssonantMetadataRetrieverError(
                "[PRE-PROCESS] CSV metadata retriever failed while converting np.nan values to None!"
            ) from e
        # Transform Name and Class column on lower case
        try:
            # Transform all 'Name' strings into lowercase to avoid type error from users
            self.df[CSVColumn.NAME.value] = self.df[CSVColumn.NAME.value].apply(lambda x: x.lower())
        except Exception as e:
            raise AssonantMetadataRetrieverError(
                f"[PRE-PROCESS] CSV metadata retriever failed while lowering {CSVColumn.NAME.value} column strings! Cause may be a row with a missing value!"
            ) from e
        try:
            # Transform all 'Subcomponent of' strings into lowercase to correctly match 'Name' that
            # has just been lowercased.
            self.df[CSVColumn.SUBCOMPONENT_OF.value] = self.df[CSVColumn.SUBCOMPONENT_OF.value].apply(
                lambda x: x.lower() if x not in self.invalid_values else x
            )
        except Exception as e:
            raise AssonantMetadataRetrieverError(
                f"[PRE-PROCESS] CSV metadata retriever failed while lowering {CSVColumn.SUBCOMPONENT_OF.value} column strings!"
            ) from e
        try:
            # Remove empty space between names to match AssonantDataClass names
            self.df[CSVColumn.CLASS.value] = self.df[CSVColumn.CLASS.value].apply(lambda x: x.replace(" ", ""))
        except Exception as e:
            raise AssonantMetadataRetrieverError(
                f"[PRE-PROCESS] CSV metadata retriever failed while concatenating {CSVColumn.CLASS.value} column strings! Cause may be a row with a missing value!"
            ) from e
        # try:
        #    # Convert Experiment class to Entry class
        #    self.df[CSVColumn.CLASS.value] = self.df[CSVColumn.CLASS.value].replace('Experiment', 'Entry')
        # except Exception as e:
        #    raise AssonantMetadataRetrieverError(
        #        "[PRE-PROCESS] CSV metadata retriever failed while converting np.nan values to None!"
        #    ) from e

    def _get_row_by_pv_name(self, pv_name: str) -> pd.DataFrame:
        """Return DataFrame row that matches the passed PV name.

        Args:
            pv_name (str): PV name that identified the target row.

        Returns:
            pd.DataFrame: DataFrame row that matches the passed pv_name.
        """
        # Find row that matches the PV name and return a copy of it
        return self.df[self.df[CSVColumn.PV_NAME.value] == pv_name].copy(deep=True)

    def _convert_acquisition_moment_into_acquisition_type(
        self, acquisition_moment: AcquisitionMoment
    ) -> AcquisitionType:
        """Convert AcquisitionMoment value to its respective AcquisitionType equivalent

        Args:
            acquisition_moment (AcquisitionMoment): AcquisitionMoment Enum object to be converted

        Raises:
            AssonantMetadataRetrieverError: Raised if there is no valid convertion for passed AcquisitionMoment.

        Returns:
            AcquisitionType: AcquisitionType Enum object respective to the passed Acquisition Moment Enum object.
        """

        mapping = {
            AcquisitionMoment.START.value: AcquisitionType.SNAPSHOT,
            AcquisitionMoment.END.value: AcquisitionType.SNAPSHOT,
        }
        try:
            converted_value = mapping[acquisition_moment.value]
        except Exception as e:
            raise AssonantMetadataRetrieverError(
                f"There is no valid AcquisitionType convertion value for '{acquisition_moment.value}' AcquisitionMoment"
            ) from e
        return converted_value

    def get_pv_names_by_acquisition_moment(self, acquisition_moment: AcquisitionMoment) -> List[str]:
        """Return a List with all PV names related to the passed AcquisitionMoment.

        PS: Check IAssonantMetadataRetriever Interface for the return structure definition!

        Args:
            acquisition_type (AcquisitionMoment): Target Acquisition Moment used for selecting which
            PV names will be returned.

        Returns:
            List[str]: List containing all PV names related to passed AcquisitionMoment.
        """
        acquisition_type = self._convert_acquisition_moment_into_acquisition_type(acquisition_moment)
        filtered_df = self.df[self.df[CSVColumn.ACQUISITION_TYPE.value] == acquisition_type.value]
        filtered_df = filtered_df = filtered_df[
            ~filtered_df[CSVColumn.PV_NAME.value].isin([""]) & filtered_df[CSVColumn.PV_NAME.value].notna()
        ]

        # Iterate over rows and append the PV name to the result List
        result = [row[CSVColumn.PV_NAME.value] for _, row in filtered_df.iterrows()]
        return result

    def get_pvs_info(self, pv_names: Union[str, List[str]]) -> Dict[str, Dict[str, Any]]:
        """Return all information about the PV paired by the its name.

        PS: Check IAssonantMetadataRetriever Interface for the return structure definition!

        Args:
            pv_names (Union[str, List[str]]): PV name or List with PV names which info will
            be fetched.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary containing all PV metadata paired by the PV name.
            If passed PV names were not found on source an empty dict {} is returned
        """
        if isinstance(pv_names, str):
            # Standardize input to treat input as list
            pv_names = [pv_names]

        filtered_df = self.df[self.df[CSVColumn.PV_NAME.value].isin(pv_names)]

        if filtered_df.empty:
            return {}
        else:
            result = {
                row[CSVColumn.PV_NAME.value]: {
                    "component_info": {
                        "name": row[CSVColumn.NAME.value],
                        "class": row[CSVColumn.CLASS.value],
                        **(
                            {"subcomponent_of": row[CSVColumn.SUBCOMPONENT_OF.value]}
                            if row[CSVColumn.SUBCOMPONENT_OF.value] not in self.invalid_values
                            else {}
                        ),
                    },
                    "data_handler_info": {
                        "name": row[CSVColumn.NEXUS_FIELD_NAME.value],
                        "value": ValuePlaceholders.VALUE_NOT_SET.value,
                        **(
                            {"unit": row[CSVColumn.UNIT_OF_MEASUREMENT.value]}
                            if row[CSVColumn.UNIT_OF_MEASUREMENT.value] not in self.invalid_values
                            else {}
                        ),
                        **(
                            {"transformation_type": row[CSVColumn.TRANSFORMATION_TYPE.value]}
                            if row[CSVColumn.TRANSFORMATION_TYPE.value] not in self.invalid_values
                            else {}
                        ),
                        "pv_name": row[CSVColumn.PV_NAME.value],
                    },
                }
                for _, row in filtered_df.iterrows()
            }

        return result

    def get_subcomponents_mapping(self) -> Dict[str, List[str]]:
        """Return a Dictionary mapping component names with the name of its subcomponents.

        PS: Check IAssonantMetadataRetriever Interface for the return structure definition!

        Returns:
            Dict[str, List[str]]: Dictionary mapping the name of each Component that contains at
            least one Subcomponent with their respective List of Subcomponents names.
        """

        filtered_df = self.df[[CSVColumn.NAME.value, CSVColumn.SUBCOMPONENT_OF.value]].dropna()

        mapping = {}

        for component_name, subcomponent_names in filtered_df.groupby(CSVColumn.SUBCOMPONENT_OF.value)[
            CSVColumn.NAME.value
        ]:
            mapping[component_name] = list(set((subcomponent_names)))

        return mapping

    def get_component_info(self, component_name: str) -> Dict[str, Dict[str, Any]]:
        """Retrieve info about a specific Component based on passed component_name.

        PS: Check IAssonantMetadataRetriever Interface for the return structure definition!

        Args:
            component_name (str): Component name to retrieve information about.

        Returns:
            Dict[str, Dict[str, Any]]: Component info dictionary following the same subdictionary
            returned by get_pvs_info() method to represent component info. If component is not
            found on source, a empty dict {} is returned.
        """
        # Transform component_name into lower() to avoid input formatting errors
        # Return only the first matching elements
        query_result = self.df[self.df[CSVColumn.NAME.value] == component_name.lower()].head(1).squeeze()

        if query_result.empty:
            return {}
        else:
            component_info = {
                "component_info": {
                    "name": query_result[CSVColumn.NAME.value],
                    "class": query_result[CSVColumn.CLASS.value],
                    **(
                        {"subcomponent_of": query_result[CSVColumn.SUBCOMPONENT_OF.value]}
                        if query_result[CSVColumn.SUBCOMPONENT_OF.value] not in self.invalid_values
                        else {}
                    ),
                }
            }
        return component_info
