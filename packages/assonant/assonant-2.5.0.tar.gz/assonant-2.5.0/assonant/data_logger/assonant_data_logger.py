from typing import Any, Dict, List, Optional, Union

from assonant.data_classes import (
    AssonantComponentFactory,
    AssonantDataHandlerFactory,
    AssonantEntryFactory,
    Entry,
)
from assonant.data_classes.components import Beamline, Component
from assonant.data_classes.data_handlers import Axis, DataHandler
from assonant.data_classes.exceptions import AxisInsertionError, FieldInsertionError
from assonant.data_retriever import AssonantDataRetriever
from assonant.file_writer import AssonantFileWriter
from assonant.hierarchizer import Hierarchizer
from assonant.metadata_retriever import AssonantMetadataRetriever
from assonant.naming_standards import AcquisitionMoment, BeamlineName, ExperimentStage
from assonant.path_builder import BeamlinePathBuilder

from ._pv_collector import PVCollector
from .exceptions import AssonantDataLoggerError

# NOTE: AssonantDataLogger can probably be classified as a GodObject at this moment.
#  Some Refactor would be good to enhance the code quality based on SOLID principles.


class AssonantDataLogger:
    """Assonant Data Logger.

    Object responsible to automate data collection, standardization and logging based on
    pré-defined configurations.
    """

    _supported_acquisition_moments_for_auto_collection = [AcquisitionMoment.START, AcquisitionMoment.END]

    def __init__(
        self,
        beamline_name: BeamlineName,
        pre_init_auto_collector_pv_connections: bool = False,
        data_schema_file_path: Optional[str] = None,
    ):
        """AssonantDataLogger Constructor.

        Args:
            beamline_name (BeamlineName): Beamline name where the experiment is being executed.
            pre_init_auto_collector_pv_connections (bool): Flag to control if connections to auto collectable PVs should
            be pre-initiallized during AssonantDataLogger instantiation or not. Defaults to False.
            data_schema_file_path (str): Path to data schema file.
        """

        self.beamline_name = beamline_name

        self.path_builder = BeamlinePathBuilder()
        self.path_builder.set_beamline_name(beamline_name.value.lower())

        if data_schema_file_path is None:
            # No data schema file path passed? - Use path_builder to create it based on beamline name
            self.data_schema_file_path = self.path_builder.build_path_to_data_schema()
        else:
            # Use passed data schema file path
            self.data_schema_file_path = data_schema_file_path

        self.metadata_retriever = AssonantMetadataRetriever(metadata_source_file_path=self.data_schema_file_path)
        self.hierarchizer = Hierarchizer(self.data_schema_file_path, self.metadata_retriever)
        self.pv_names = {}
        self.pv_collectors = {}
        self.file_writer = AssonantFileWriter("nexus")
        self.pv_collectors_innitialized = False

        if pre_init_auto_collector_pv_connections is True:
            self.init_auto_collector()

    def _create_data_handler_from_pv_info(self, pv_info: Dict[str, Dict[str, Any]]) -> DataHandler:
        """Create data handler based on passed pv_info Dict.

        Args:
            pv_info (Dict[str, Dict[str, Any]]): Dict containing acquired PV info. The Dict follows must follow
            the structure proposed for the get_pvs_info() call from the IAssonantDataRetriever Interface.

        Returns:
            DataHandler: Specific DataHandler related to the passed info.
        """
        param_names = ["value", "unit", "transformation_type", "timestamps", "timestamps_unit"]
        ignored = ["name"]
        extra_metadata = {}
        params = {}

        # Search into dict which names are parameters for the create method from factory, the rest
        # is considered as extra_metadata
        data_handler_info = pv_info["data_handler_info"]
        for info_name in data_handler_info:
            if info_name not in ignored:
                if info_name not in param_names:
                    extra_metadata[info_name] = data_handler_info[info_name]
                else:
                    params[info_name] = data_handler_info[info_name]

        params["extra_metadata"] = extra_metadata

        return AssonantDataHandlerFactory.create_data_handler(**params)

    def _add_fields_to_component(self, component: Component, fields: Dict[str, DataHandler]):
        """Add fields from dict to passed Component.

        Args:
            component (Component): Component which fields will be inserted to.
            fields (dict[str, DataHandler]): Dict of fields that will be inserted on component.
        """
        for field_name in fields:
            try:
                component.add_field(name=field_name, new_field=fields[field_name])
            except FieldInsertionError:
                # To avoid breaking and not logging other data, errors in insertion are ignored and logged
                # TODO: Put this into a log file instead of printing it
                print(
                    f"{field_name} field was not add to {component.name} due to an Error during its insertion on fields dict"
                )

    def _add_positions_to_component(self, component: Component, positions: Dict[str, Axis]):
        """Add axis from dict to passed Component.

        Args:
            component (Component): Component which axis will be inserted to.
            positions (dict[str, Axis]): Dict of axis that will be inserted on component.
        """
        for axis_name in positions:
            try:
                component.add_position(name=axis_name, new_axis=positions[axis_name])
            except AxisInsertionError:
                # To avoid breaking and not logging other data, errors in insertion are ignored and logged
                # TODO: Put this into a log file instead of printing it
                print(
                    f"{axis_name} Axis was not add to {component.name} due to an Error during its insertion on positions dict"
                )

    def _create_component_from_pv_info(self, pv_info: Dict[str, Dict[str, Any]]) -> Component:
        """Create an Assonant Component based on passed dict with PV data.

        Args:
            pv_info (Dict[str, Dict[str, Any]]): Dict containing Component info retrieved from pv_info dict.
            The passed dict must follow the structure defined on get_pvs_info() method from IAssonantDataRetriever.

        Returns:
            Component: Assonant Component respective to passed PV data.
        """
        component_info = pv_info["component_info"]
        return AssonantComponentFactory.create_component_by_class_name(
            class_name=component_info["class"], component_name=component_info["name"]
        )

    def _wrap_components_into_entry(self, components: List[Component], entry: Entry) -> Entry:
        """Wrap components into a Entry object based on the AcquisitionMoment.

        Args:
            components (List[Component]): List of Components to wrap into the Entry object.
            entry (Entry): Entry which Components will be add to.

        Returns:
            Entry: Entry containing all passed components within a Beamline object.
        """
        for component in components:

            if isinstance(component, Entry):
                # Special case: Metadata related to Entry must be added to pre-created instance
                entry.take_data_handlers_from(entry=component)
            elif isinstance(component, Beamline):
                # Special case: Metadata related to beamline must be added to pre-created instance
                entry.beamline.take_data_handlers_from(component=component)
            else:
                entry.beamline.add_subcomponent(component)

        return entry

    def init_auto_collector(self):
        """Pre-establish PV collectors connections for auto collection functionality.

        Recommended to avoid having to establish connection with all PVs during a collect call.
        """

        acquisition_moments = [AcquisitionMoment.START, AcquisitionMoment.END]

        for acquisition_moment in acquisition_moments:

            # Try to retrieve PV names that will be collect on Acquisition Moment
            try:
                self.pv_names[acquisition_moment.value] = self.metadata_retriever.get_pv_names_by_acquisition_moment(
                    acquisition_moment
                )
            except Exception as e:
                raise AssonantDataLoggerError(
                    f"Failed to retrieve PV names for '{acquisition_moment.value}' Acquisition Moment!"
                ) from e

            # Try to initialize connection retrieve PVs
            try:
                self.pv_collectors[acquisition_moment.value] = PVCollector(self.pv_names[acquisition_moment.value])
            except Exception as e:
                raise AssonantDataLoggerError(
                    f"Faield to initialize PVCollector for PVs from '{acquisition_moment.value}' Acquisition Moment!"
                ) from e

        # Update PV collector status flag
        self.pv_collectors_innitialized = True

    def collect_and_log_pv_data(
        self,
        log_file_path: str,
        log_file_name: str,
        experiment_stage: ExperimentStage,
        acquisition_moment: AcquisitionMoment,
    ):
        """Trigger data logger to collect PV data based on AcquisitionMoment, standardize it and log it.

        Args:
            log_file_path (str): Path where log file will be saved.
            log_file_name (str): Name of the log file that will be saved on log_file_path.
            acquisition_moment (AcquisitionMoment): AcquisitionMoment which PV data will be collected and logged.

        """
        if acquisition_moment in self._supported_acquisition_moments_for_auto_collection:
            if self.pv_collectors_innitialized is False:
                self.init_auto_collector()
            acquired_pv_data = self.pv_collectors[acquisition_moment.value].acquire_data()
            self.log_collected_pv_data(
                log_file_path=log_file_path,
                log_file_name=log_file_name,
                experiment_stage=experiment_stage,
                acquisition_moment=acquisition_moment,
                pv_data=acquired_pv_data,
            )
        else:
            raise AssonantDataLoggerError(
                f"Experimental stage '{acquisition_moment.value}' is not supported yet for auto collection! Use the log_collected_data method instead!"
            )

    def log_collected_pv_data(
        self,
        log_file_path: str,
        log_file_name: str,
        experiment_stage: ExperimentStage,
        acquisition_moment: AcquisitionMoment,
        pv_data: Dict[str, Any],
    ):
        """Standardize and log collected PV data represented as {PV_NAME: COLLECTED_VALUE} Dict.

        Args:
            log_file_path (str): Path where log file will be saved.
            log_file_name (str): Name of the log file that will be saved on log_file_path.
            acquisition_moment (AcquisitionMoment): Current AcquisitionMoment which data was collected.
            pv_data (Dict[str, Any]): Collected PV data. The Dict structure must follow the same data structure
            and representation as the PVCollector acquire_data() method.
        """
        pv_names = [pv_name for pv_name in pv_data.keys()]
        pv_name_and_info_mapping = self.metadata_retriever.get_pvs_info(pv_names=pv_names)
        components = {}

        # Create DataHandlers for each acquired PV
        for pv_name, pv_info in pv_name_and_info_mapping.items():

            # Create DataHandler for PV field
            data_handler = self._create_data_handler_from_pv_info(pv_info)
            data_handler.set_value(pv_data[pv_name])
            data_handler_name = pv_info["data_handler_info"]["name"]

            component_name = pv_info["component_info"]["name"]

            # Create Component if doesn't already exist
            if component_name not in components.keys():
                components[component_name] = self._create_component_from_pv_info(pv_info)

            components[component_name].add_data_handler(name=data_handler_name, new_data_handler=data_handler)

        hierarchized_components = self.hierarchizer.hierarchize_components(list(components.values()))

        entry_name = "_".join([experiment_stage.value, acquisition_moment.value])
        entry = AssonantEntryFactory.create_entry(entry_name, self.beamline_name)
        entry = self._wrap_components_into_entry(hierarchized_components, entry)

        self.file_writer.write_data(log_file_path, log_file_name, entry)

    def log_collected_component_data(
        self,
        log_file_path: str,
        log_file_name: str,
        experiment_stage: ExperimentStage,
        acquisition_moment: AcquisitionMoment,
        components: Union[Component, List[Component]],
    ):
        """Standardize and log collected PV data already wrapped as Assonant Components.

        Args:
            log_file_path (str): Path where log file will be saved.
            log_file_name (str): Name of the log file that will be saved on log_file_path.
            acquisition_moment (AcquisitionMoment): Current AcquisitionMoment which data was collected.
            components (Union[Component, List[Component]]): List of Assonant Component objects with data to be logged.
        """
        print(
            "WARNING: LOG_COLLECTED_COMPONENT_DATA METHOD IS DISCOURAGED DUE TO THE LACK OF AUTOMATION AND"
            + "LACK OF COMPONENTS HIERARCHY STANDARDIZATION. ONLY USE THIS IF YOU ARE REALLY SURE"
            + "IN WHAT YOU ARE DOING!!!"
        )
        if isinstance(components, Component):
            components = [components]

        entry_name = "_".join([experiment_stage.value, acquisition_moment.value])
        entry = AssonantEntryFactory.create_entry(entry_name, self.beamline_name)
        entry = self._wrap_components_into_entry(components, entry)

        self.file_writer.write_data(log_file_path, log_file_name, entry)

    def log_bluesky_data_from_json_file(
        self,
        log_file_path: str,
        log_file_name: str,
        experiment_stage: ExperimentStage,
        acquisition_moment: AcquisitionMoment,
        json_file_path: str,
    ):
        """Log bluesky data on json files into a standardize way

        Args:
            log_file_path (str): Path where log file will be saved.
            log_file_name (str): Name of the log file that will be saved on log_file_path.
            experiment_stage (ExperimentStage): Enum related to the ExperimentStage in which the data was collected.
            acquisition_moment (AcquisitionMoment): Enum related to the AcquisitionMoment that data was collected
            within the ExperimentStage.
            json_file_path (str): Path to the json file containing the bluesky data.
        """

        # TODO: POSSIBLE ENHANCEMENT: FUTURALLY, DEPENDING ON PERFORMANCE REQUIREMENTS, SOME KIND OF CONTROL
        # IF INSTANTIATES A NEW BLUESKY DATA PARSER OR REUSE AN ALREADY EXISTING ONE MAY BE GOOD. THIS
        # WAY IT AVOIDS PROCESSING MULTUIPLE TIMES THE SAME DOCUMMENTS TO FIND THE SAME DATA.
        assonant_data_retriever = AssonantDataRetriever(data_source=json_file_path)

        pv_data = assonant_data_retriever.get_pv_data_by_acquisition_moment(acquisition_moment)
        # print(pv_data)
        self.log_collected_pv_data(log_file_path, log_file_name, experiment_stage, acquisition_moment, pv_data)

    def log_bluesky_data_from_documents_list(
        self,
        log_file_path: str,
        log_file_name: str,
        experiment_stage: ExperimentStage,
        acquisition_moment: AcquisitionMoment,
        documents_list: List[List[Union[str, Dict[str, Any]]]],
    ):
        """Log bluesky data passed as a dict of bluesky documments (which are also represented as dicts)

        Args:
            log_file_path (str): Path where log file will be saved.
            log_file_name (str): Name of the log file that will be saved on log_file_path.
            experiment_stage (ExperimentStage): Enum related to the ExperimentStage in which the data was collected.
            acquisition_moment (AcquisitionMoment): Enum related to the AcquisitionMoment that data was collected
            within the ExperimentStage.
            documents_list (List[List[Union[str, Dict[str, Any]]]]): List of bluesky documents data presented also as
            a list. The list with the document data has 2 positions, the 1st is the bluesky identification for the
            document (start, event, stop, descriptor, ...) and the 2nd position the dict containing the document
            data.
        """

        # TODO: POSSIBLE ENHANCEMENT: FUTURALLY, DEPENDING ON PERFORMANCE REQUIREMENTS, SOME KIND OF CONTROL
        # IF INSTANTIATES A NEW BLUESKY DATA PARSER OR REUSE AN ALREADY EXISTING ONE MAY BE GOOD. THIS
        # WAY IT AVOIDS PROCESSING MULTUIPLE TIMES THE SAME DOCUMMENTS TO FIND THE SAME DATA.
        assonant_data_retriever = AssonantDataRetriever(data_source=documents_list)

        pv_data = assonant_data_retriever.get_pv_data_by_acquisition_moment(acquisition_moment)
        # print(pv_data)
        self.log_collected_pv_data(log_file_path, log_file_name, experiment_stage, acquisition_moment, pv_data)
