"""
Tests focused on validating AssonantDataLogger methods

This tests must not verify correct behavior of underlying modules
as that is part of their domain-specific test. This must only
validate AssonantDataLogger does not break during the
the coordination of the usage of all its components.
"""

import json
import os

import numpy as np
import pytest
from nexusformat.nexus.tree import nxload

from assonant.data_classes.components import Mirror, Monochromator, MonochromatorCrystal
from assonant.data_classes.enums import TransformationType
from assonant.data_classes.factories import AssonantComponentFactory
from assonant.data_logger import AssonantDataLogger
from assonant.data_logger.exceptions import AssonantDataLoggerError
from assonant.naming_standards import AcquisitionMoment, BeamlineName, ExperimentStage

from ..utils import assert_n_files_exists_in_dir, get_fixture_values


# --------------------
# Fixtures
# --------------------
@pytest.fixture(scope="session")
def data_logger_pre_init_auto_collect(example_csv_metadata_file_path):
    """
    Provides a AssonantDataLogger configures to access metadata from example csv file
    and with the pre_init_aut_collector_pv_connections config on.
    """
    logger = AssonantDataLogger(
        BeamlineName.CATERETE,
        pre_init_auto_collector_pv_connections=True,
        data_schema_file_path=example_csv_metadata_file_path,
    )
    return logger


@pytest.fixture(scope="function")
def data_logger(example_csv_metadata_file_path):
    """
    Provides a AssonantDataLogger configures to access metadata from example csv file
    and with the pre_init_aut_collector_pv_connections config off.
    """
    logger = AssonantDataLogger(BeamlineName.CATERETE, data_schema_file_path=str(example_csv_metadata_file_path))
    return logger


@pytest.fixture(scope="session")
def example_collected_pvs():
    """
    Provides a simulated dict containing simulated data acquired for PVs from
    the example metadata csv.
    """
    return {
        "ATTENUATOR_PV": 10,
        "APERTURE_PV": "Test Repeatition",
        "BEAM_PV": None,
        "BEAM STOPPER_PV": [1, 2, 3, 4, 5, 6],
        "COLLIMATOR_PV": 1.2,
        "MIRROR_PV": np.array([1, 2, None, 4, 5]),
        "THIS_PV_DONT_EXIST": "Test",
    }


@pytest.fixture(scope="session")
def example_collected_component_with_none_values():
    """
    Provides a simulated collected component with DataHandlers containing None value within it simulating
    may collection failure cases
    """
    mirror_with_none_values = AssonantComponentFactory.create_component_by_class_type(Mirror, "none_values_mirror")
    mirror_with_none_values.create_and_add_position(
        name="x", transformation_type=TransformationType.TRANSLATION, value=None, unit="cm"
    )
    mirror_with_none_values.create_and_add_position(
        name="y", transformation_type=TransformationType.TRANSLATION, value=[7.5, 8.0, 9.0]
    )
    mirror_with_none_values.create_and_add_position(
        name="Ry", transformation_type=TransformationType.ROTATION, value=[7.5, None, 9.0]
    )
    mirror_with_none_values.create_and_add_timeseries_position(
        name="z",
        transformation_type=TransformationType.TRANSLATION,
        value=[1, 2, 3, 4, 5],
        timestamps=[0.1, 0.2, None, 0.4, 0.5],
    )
    mirror_with_none_values.create_and_add_field(name="field1", value="some information")
    mirror_with_none_values.create_and_add_field(name="field2", value=["1", "2", None, "4", "5"], unit="GeV")

    return mirror_with_none_values


@pytest.fixture(scope="function")
def example_collected_component_with_subcomponent():
    """
    Provides a simulated collected component with subcomponent
    """
    monoch_crystal = AssonantComponentFactory.create_component_by_class_type(MonochromatorCrystal, "crystal_2")
    monoch_crystal.create_and_add_position(
        name="y", transformation_type=TransformationType.TRANSLATION, value=[7.5, 8.0, 9.0]
    )
    monoch_crystal.create_and_add_timeseries_position(
        name="z",
        transformation_type=TransformationType.TRANSLATION,
        value=[1, 2, 3, 4, 5],
        timestamps=[0.1, 0.2, 0.3, 0.4, 0.5],
    )
    monoch_crystal.create_and_add_position(
        name="Rx", transformation_type=TransformationType.ROTATION, value=20, unit="rad"
    )
    monoch_crystal.create_and_add_field(name="temperature", value=30, unit="K")

    monoch = AssonantComponentFactory.create_component_by_class_type(Monochromator, "mono_fields")
    monoch.add_subcomponent(monoch_crystal)
    monoch.create_and_add_field(name="wavelength", value=[10, 20, 30, 40], unit="db")
    monoch.create_and_add_field(
        name="energy",
        value=10,
        extra_metadata={
            "attr1": 10,
            "attr2": "atributo 2",
            "attr3": 0.765,
            "attr4": [1, 2, 3, 4, 5],
        },
    )

    return monoch


@pytest.fixture(scope="function")
def example_collected_component_without_subcomponent():
    mirror = Monochromator(name="mirror")
    mirror.create_and_add_field(name="field_1", value=[10, 20, 30, 40], unit="u")
    mirror.create_and_add_field(
        name="field_2",
        value=10,
        extra_metadata={
            "attr1": 10,
            "attr2": "atributo 2",
            "attr3": 0.765,
            "attr4": [1, 2, 3, 4, 5],
        },
    )

    return mirror


# --------------------
# Tests
# --------------------


def test_auto_collect_pv_data(data_logger_pre_init_auto_collect, tmp_path):
    """
    Validate that AssonantDataLogger works correctly and don't break
    when using its pv data auto_collection feature for Start and End Acquisition
    Moments.

    PS: Content is not being validated only if module does not break!

    Expected Behavior:
        - AssonantDatalogger must create a new NeXus file into target file path with the given file name
    """
    log_file_path = tmp_path
    log_file_name = "test_file.nxs"

    # START & END acq_moments
    data_logger_pre_init_auto_collect.collect_and_log_pv_data(
        log_file_path, log_file_name, ExperimentStage.SAMPLE_ACQUISITION, AcquisitionMoment.START
    )
    data_logger_pre_init_auto_collect.collect_and_log_pv_data(
        log_file_path, log_file_name, ExperimentStage.SAMPLE_ACQUISITION, AcquisitionMoment.END
    )

    assert_n_files_exists_in_dir(1, log_file_path)
    assert os.path.exists(os.path.join(log_file_path, log_file_name))


def test_auto_collect_pv_data_failure_for_during_acq_moment(data_logger_pre_init_auto_collect, tmp_path):
    """
    Validate that AssonantDataLogger fails when trying to use its pv data auto_collection feature
    for during AcquisitionMoment.

    PS: This must happens as this features is not implement and there isn't current plan to develop it!

    Expected Behavior:
        - AssonantDatalogger must raise an AssonantDatLoggerError informing the feature is not
        supported.
    """
    log_file_path = tmp_path
    log_file_name = "test_file.nxs"

    # DURING should raise error
    with pytest.raises(AssonantDataLoggerError):
        data_logger_pre_init_auto_collect.collect_and_log_pv_data(
            log_file_path, log_file_name, ExperimentStage.SAMPLE_ACQUISITION, AcquisitionMoment.DURING
        )


def test_log_collected_pvs(data_logger, example_collected_pvs, tmp_path):
    """
    Validate that AssonantDataLogger works correctly and don't break when using
    its method to log collect PV data for existing AcquisitionMoments.

    PS: Content is not being validated only if module does not break!

    Expected Behavior:
        - AssonantDatalogger must create a new NeXus file into target file path with the given file name
    """
    log_file_path = tmp_path
    log_file_name = "test_file.nxs"

    for acq_moment in AcquisitionMoment:
        data_logger.log_collected_pv_data(
            log_file_path, log_file_name, ExperimentStage.SAMPLE_ACQUISITION, acq_moment, example_collected_pvs
        )

    assert_n_files_exists_in_dir(1, log_file_path)
    assert os.path.exists(os.path.join(log_file_path, log_file_name))


def test_log_empty_pvs_dict(data_logger, tmp_path):
    """
    Validate that AssonantDataLogger works correctly and don't break when using
    its method to log collect PV data for existing AcquisitionMoments but data dict
    is empty.

    PS: Content is not being validated only if module does not break!

    Expected Behavior:
        - AssonantDatalogger must create a new NeXus file into target file path with the given file name
    """
    log_file_path = tmp_path
    log_file_name = "test_file.nxs"

    for acq_moment in [AcquisitionMoment.START, AcquisitionMoment.END, AcquisitionMoment.DURING]:
        data_logger.log_collected_pv_data(
            log_file_path, log_file_name, ExperimentStage.SAMPLE_ACQUISITION, acq_moment, {}
        )


def test_log_component_list(
    data_logger,
    example_collected_component_with_subcomponent,
    example_collected_component_without_subcomponent,
    tmp_path,
):
    """
    Validate that AssonantDataLogger works correctly and don't break when using
    its method to log collect data represented within Assonant Componets wrapped
    in a list.

    PS: Content is not being validated only if module does not break!

    Expected Behavior:
        - AssonantDatalogger must create a new NeXus file into target file path with the given file name
    """
    log_file_path = tmp_path
    log_file_name = "test_file.nxs"

    component_list = [example_collected_component_with_subcomponent, example_collected_component_without_subcomponent]

    for acq_moment in AcquisitionMoment:
        data_logger.log_collected_component_data(
            log_file_path, log_file_name, ExperimentStage.SAMPLE_ACQUISITION, acq_moment, component_list
        )
    assert_n_files_exists_in_dir(1, log_file_path)
    assert os.path.exists(os.path.join(log_file_path, log_file_name))


def test_log_single_component(data_logger, example_collected_component_without_subcomponent, tmp_path):
    """
    Validate that AssonantDataLogger works correctly and don't break when using
    its method to log collect data represented within Assonant Componets and a
    single Component is passed.

    PS: Content is not being validated only if module does not break!

    Expected Behavior:
        - AssonantDatalogger must create a new NeXus file into target file path with the given file name
    """
    log_file_path = tmp_path
    log_file_name = "test_file.nxs"

    for acq_moment in AcquisitionMoment:
        data_logger.log_collected_component_data(
            log_file_path,
            log_file_name,
            ExperimentStage.SAMPLE_ACQUISITION,
            acq_moment,
            example_collected_component_without_subcomponent,
        )


def test_auto_and_manual_pv_collection(data_logger_pre_init_auto_collect, example_collected_pvs, tmp_path):
    log_file_path = tmp_path
    log_file_name = "test_file.nxs"

    data_logger_pre_init_auto_collect.collect_and_log_pv_data(
        log_file_path, log_file_name, ExperimentStage.SAMPLE_ACQUISITION, AcquisitionMoment.START
    )
    data_logger_pre_init_auto_collect.log_collected_pv_data(
        log_file_path,
        log_file_name,
        ExperimentStage.SAMPLE_ACQUISITION,
        AcquisitionMoment.DURING,
        example_collected_pvs,
    )
    data_logger_pre_init_auto_collect.collect_and_log_pv_data(
        log_file_path, log_file_name, ExperimentStage.SAMPLE_ACQUISITION, AcquisitionMoment.END
    )


@pytest.mark.parametrize(
    "bluesky_path_fixture_name",
    [
        "example_bluesky_baseline_acquisition_file_path",
        "example_bluesky_primary_acquisition_file_path",
        "example_bluesky_monitor_acquisition_file_path",
    ],
)
def test_log_bluesky_acquisition_from_json_file(data_logger, bluesky_path_fixture_name, tmp_path, request):
    """
    Validate that AssonantDataLogger works correctly and don't break when using
    its method to log bluesky collected data within passed JSON file.

    PS: Content is not being validated only if module does not break!

    Expected Behavior:
        - AssonantDatalogger must create a new NeXus file into target file path with the given file name
        - For each existing AcquisitionMoment, one Entry must have been created within the file.
    """
    log_file_path = tmp_path
    log_file_name = "test_file.nxs"
    exp_stage = ExperimentStage.SAMPLE_ACQUISITION

    # Get the fixture value dynamically
    example_bluesky_file_path = get_fixture_values(bluesky_path_fixture_name, request)

    # Run log for each acquisition moment
    for acq_moment in AcquisitionMoment:
        data_logger.log_bluesky_data_from_json_file(
            log_file_path,
            log_file_name,
            exp_stage,
            acq_moment,
            example_bluesky_file_path,
        )

    # Assert that only one file was created
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].name == log_file_name

    # Assert that 1 entry was created for each acquisition moment
    nxroot = nxload(os.path.join(log_file_path, log_file_name), mode="r")
    assert len(nxroot.entries) == len(AcquisitionMoment)


@pytest.mark.parametrize(
    "bluesky_path_fixture_name",
    [
        "example_bluesky_baseline_acquisition_file_path",
        "example_bluesky_primary_acquisition_file_path",
        "example_bluesky_monitor_acquisition_file_path",
    ],
)
def test_log_bluesky_acquisition_from_docs_list(data_logger, bluesky_path_fixture_name, tmp_path, request):
    """
    Validate that AssonantDataLogger works correctly and don't break when using
    its method to log bluesky collected data within list of bluesky docs
    read from the JSON file.

    PS: Content is not being validated only if module does not break!

    Expected Behavior:
        - AssonantDatalogger must create a new NeXus file into target file path with the given file name
        - For each existing AcquisitionMoment, one Entry must have been created within the file.
    """
    log_file_path = tmp_path
    log_file_name = "test_file.nxs"
    exp_stage = ExperimentStage.SAMPLE_ACQUISITION

    # Get the fixture value dynamically
    example_bluesky_file_path = get_fixture_values(bluesky_path_fixture_name, request)
    with open(example_bluesky_file_path) as f:
        example_bluesky_docs_list = json.load(f)

    # Run log for each acquisition moment
    for acq_moment in AcquisitionMoment:
        data_logger.log_bluesky_data_from_documents_list(
            log_file_path,
            log_file_name,
            exp_stage,
            acq_moment,
            example_bluesky_docs_list,
        )

    # Assert that only one file was created
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].name == log_file_name

    # Assert that 1 entry was created for each acquisition moment
    nxroot = nxload(os.path.join(log_file_path, log_file_name), mode="r")
    assert len(nxroot.entries) == len(AcquisitionMoment)
