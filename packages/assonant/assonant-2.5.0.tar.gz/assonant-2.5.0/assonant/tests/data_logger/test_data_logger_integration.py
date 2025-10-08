"""
Tests focused on validating AssonantDataLogger integration in beamlines

This tests will evaluate AssonantDataLogger functionalities with some real data
and real metadata.csv files from beamlines. The goal here is to verify if nothing will
break when going to production in the beamline.
"""

import json
import os

import pytest

from assonant.data_logger import AssonantDataLogger
from assonant.naming_standards import AcquisitionMoment, BeamlineName, ExperimentStage

from ..utils import assert_n_files_exists_in_dir

# To avoid leaking this IPs on PyPi, this must be set manually!!!
# This must be a dict where the keys are the BeamlineName and the value
# a string listing the IPs as following -> "<IP_1> <IP_2> <IP_3>..."
EPICS_CA_ADDR_LIST_MAPPING = None


@pytest.mark.parametrize("beamline_name", [beamline_name for beamline_name in BeamlineName])
@pytest.mark.forked  # This is MANDATORY for this test to correctly isolate env variables for EPICS_CA_ADDR_LIST
def test_collect_and_log_nexus_file_with_real_beamline_csv_metadata_files(
    beamline_name, real_csv_metadata_file_path_map, tmp_path, monkeypatch
):
    """
    Validate that AssonantDataLogger works correctly when using real beamline
    csv metadata. The collect_and_log method is used to allow some real acquisition
    and logging to happen, so also validates the log process with real data.

    PS: Content is not being validated only if module does not break!

    Expected Behavior:
        - For each beamline_name;
            - AssonantDatalogger must create a new NeXus file into target file path with the given file name
    """
    log_file_path = tmp_path

    if EPICS_CA_ADDR_LIST_MAPPING is None:
        pytest.skip(reason="EPICS_CA_ADDR_LIST_MAPPING was not set!")
    elif not os.path.exists(real_csv_metadata_file_path_map[beamline_name.value]):
        pytest.skip(reason=f"CSV metadata for {beamline_name} does not exist yet")
    elif beamline_name.value not in EPICS_CA_ADDR_LIST_MAPPING.keys():
        pytest.skip(reason=f"EPICS_CA_ADDR_LIST_MAPPING does not contain addresses for {beamline_name} beamline yet")
    else:

        log_file_name = f"test_{beamline_name.value}_file"
        monkeypatch.delenv("EPICS_CA_ADDR_LIST", raising=False)
        monkeypatch.setenv("EPICS_CA_ADDR_LIST", EPICS_CA_ADDR_LIST_MAPPING[beamline_name.value])

        data_logger = AssonantDataLogger(
            beamline_name,
            pre_init_auto_collector_pv_connections=True,
            data_schema_file_path=real_csv_metadata_file_path_map[beamline_name.value],
        )

        data_logger.collect_and_log_pv_data(
            log_file_path, log_file_name, ExperimentStage.SAMPLE_ACQUISITION, AcquisitionMoment.START
        )
        data_logger.collect_and_log_pv_data(
            log_file_path, log_file_name, ExperimentStage.SAMPLE_ACQUISITION, AcquisitionMoment.END
        )

        # Assert correct number of file were created with expected names
        assert_n_files_exists_in_dir(1, log_file_path)
        assert os.path.exists(os.path.join(log_file_path, log_file_name) + ".nxs")


@pytest.mark.parametrize("beamline_name", [beamline_name for beamline_name in BeamlineName])
@pytest.mark.forked  # This is MANDATORY for this test to correctly isolate env variables for EPICS_CA_ADDR_LIST
def test_log_nexus_file_from_real_bluesky_data_files_from_files(
    beamline_name, real_csv_metadata_file_path_map, tmp_path, real_bluesky_data_test_cases_dir_path_map
):
    """
    Validate that AssonantDataLogger works correctly when using real beamline
    csv metadata to log real beamline bluesky data if directly accessing
    bluesky json files.

    PS: Content is not being validated only if module does not break!

    Expected Behavior:
        - Tests must be manually evaluated as expected behavior may vary among test cases
    """
    if not os.path.exists(real_csv_metadata_file_path_map[beamline_name.value]):
        pytest.skip(reason=f"CSV metadata for {beamline_name} does not exist yet!")
    elif beamline_name.value not in real_bluesky_data_test_cases_dir_path_map.keys():
        pytest.skip(reason=f"There is no test case with real data for {beamline_name} beamline yet!")
    else:
        log_file_name = f"test_{beamline_name.value}_file"

        data_logger = AssonantDataLogger(
            beamline_name,
            pre_init_auto_collector_pv_connections=False,
            data_schema_file_path=real_csv_metadata_file_path_map[beamline_name.value],
        )

        for i in range(0, len(real_bluesky_data_test_cases_dir_path_map[beamline_name.value])):
            # Execute test for each test case dir that exist for that beamline
            test_case_dir = real_bluesky_data_test_cases_dir_path_map[beamline_name.value][i]
            log_file_path = tmp_path / f"test_case_{i}"

            for test_case_file in os.scandir(test_case_dir):
                if test_case_file.is_file() and test_case_file.name.endswith(".json"):
                    data_logger.log_bluesky_data_from_json_file(
                        log_file_path,
                        log_file_name,
                        ExperimentStage.SAMPLE_ACQUISITION,
                        AcquisitionMoment.START,
                        test_case_file.path,
                    )
                    data_logger.log_bluesky_data_from_json_file(
                        log_file_path,
                        log_file_name,
                        ExperimentStage.SAMPLE_ACQUISITION,
                        AcquisitionMoment.END,
                        test_case_file.path,
                    )
                    data_logger.log_bluesky_data_from_json_file(
                        log_file_path,
                        log_file_name,
                        ExperimentStage.SAMPLE_ACQUISITION,
                        AcquisitionMoment.DURING,
                        test_case_file.path,
                    )


@pytest.mark.parametrize("beamline_name", [beamline_name for beamline_name in BeamlineName])
@pytest.mark.forked  # This is MANDATORY for this test to correctly isolate env variables for EPICS_CA_ADDR_LIST
def test_log_nexus_file_from_real_bluesky_data_files_from_documents_list(
    beamline_name, real_csv_metadata_file_path_map, tmp_path, real_bluesky_data_test_cases_dir_path_map
):
    """
    Validate that AssonantDataLogger works correctly when using real beamline
    csv metadata to log real beamline bluesky data if directly accessing
    bluesky json files.

    PS: Content is not being validated only if module does not break!

    Expected Behavior:
        - Tests must be manually evaluated as expected behavior may vary among test cases
    """
    if not os.path.exists(real_csv_metadata_file_path_map[beamline_name.value]):
        pytest.skip(reason=f"CSV metadata for {beamline_name} does not exist yet!")
    elif beamline_name.value not in real_bluesky_data_test_cases_dir_path_map.keys():
        pytest.skip(reason=f"There is no test case with real data for {beamline_name} beamline yet!")
    else:
        log_file_name = f"test_{beamline_name.value}_file"

        data_logger = AssonantDataLogger(
            beamline_name,
            pre_init_auto_collector_pv_connections=False,
            data_schema_file_path=real_csv_metadata_file_path_map[beamline_name.value],
        )

        for i in range(0, len(real_bluesky_data_test_cases_dir_path_map[beamline_name.value])):
            # Execute test for each test case dir that exist for that beamline
            test_case_dir = real_bluesky_data_test_cases_dir_path_map[beamline_name.value][i]
            log_file_path = tmp_path / f"test_case_{i}"

            for test_case_file in os.scandir(test_case_dir):
                if test_case_file.is_file() and test_case_file.name.endswith(".json"):

                    with open(test_case_file) as f:
                        test_case_file_data = json.load(f)

                    data_logger.log_bluesky_data_from_documents_list(
                        log_file_path,
                        log_file_name,
                        ExperimentStage.SAMPLE_ACQUISITION,
                        AcquisitionMoment.START,
                        test_case_file_data,
                    )
                    data_logger.log_bluesky_data_from_documents_list(
                        log_file_path,
                        log_file_name,
                        ExperimentStage.SAMPLE_ACQUISITION,
                        AcquisitionMoment.END,
                        test_case_file_data,
                    )
                    data_logger.log_bluesky_data_from_documents_list(
                        log_file_path,
                        log_file_name,
                        ExperimentStage.SAMPLE_ACQUISITION,
                        AcquisitionMoment.DURING,
                        test_case_file_data,
                    )
