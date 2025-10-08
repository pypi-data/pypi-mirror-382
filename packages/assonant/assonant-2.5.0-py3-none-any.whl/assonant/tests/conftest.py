import importlib
import inspect
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Generator, List, Union

import numpy as np
import pandas as pd
import pytest
from nexusformat.nexus import *

from assonant.data_classes import Entry
from assonant.data_classes.components import *
from assonant.data_classes.components import Component
from assonant.data_classes.data_handlers import Axis, DataField, DataHandler, TimeSeries
from assonant.data_classes.enums import TransformationType
from assonant.data_classes.factories import (
    AssonantComponentFactory,
    AssonantDataHandlerFactory,
    AssonantEntryFactory,
)
from assonant.naming_standards import BeamlineName


@pytest.fixture(scope="session")
def real_bluesky_data_test_cases_dir_path_map():
    """
    Provides a pytest fixture returning a mapping where the key is the beamline
    name (str) and the value is a list of directories containing the real test
    data for that beamline.

    Example:
        {
            "carnauba": [Path(".../carnauba_test_3")],
            "manaca": [Path(".../manaca_test_4")],
            "sapucaia": [
                Path(".../sapucaia_test_1"),
                Path(".../sapucaia_test_2")
            ],
        }
    """
    base_dir = Path(__file__).parent / "data" / "real_data" / "bluesky"
    path_mapping = defaultdict(list)

    for subdir in base_dir.iterdir():
        if subdir.is_dir() and "_test_" in subdir.name:
            beamline = subdir.name.split("_test_")[0]
            path_mapping[beamline.upper()].append(subdir)

    return dict(path_mapping)


@pytest.fixture(scope="session")
def real_csv_metadata_file_path_map() -> str:
    """
    Provides as a pytest fixture a dict where the key is the beamline name and
    the value is the respective filepath for the real metadata.csv files for [
    integration tests.
    """
    path_mapping = {}
    for beamline_name in BeamlineName:
        path_mapping[beamline_name.value] = str(
            Path(__file__).parent / "data" / "real_data" / "csv" / beamline_name.value.lower() / "metadata.csv"
        )
    return path_mapping


@pytest.fixture(scope="session")
def example_csv_metadata_file_path() -> str:
    """
    Provides as a pytest fixture the path for the example_metadata.csv file used for tests.
    """
    return str(Path(__file__).parent / "data" / "dummy_data" / "example_metadata.csv")


@pytest.fixture(scope="session")
def example_bluesky_baseline_acquisition_file_path() -> str:
    """
    Provides as a pytest fixture the path for the example_bluesky_baseline_acquisition.json
    file used for tests, that data simulating a bluesky baseline acquisition.
    """
    return str(Path(__file__).parent / "data" / "dummy_data" / "example_bluesky_baseline_acquisition.json")


@pytest.fixture(scope="session")
def example_bluesky_primary_acquisition_file_path() -> str:
    """
    Provides as a pytest fixture the path for the example_bluesky_primary_acquisition.json file used for tests.
    """
    return str(Path(__file__).parent / "data" / "dummy_data" / "example_bluesky_primary_acquisition.json")


@pytest.fixture(scope="session")
def example_bluesky_monitor_acquisition_file_path() -> str:
    """
    Provides as a pytest fixture the path for the example_bluesky_monitor_acquisition.json file used for tests.
    """
    return str(Path(__file__).parent / "data" / "dummy_data" / "example_bluesky_monitor_acquisition.json")


@pytest.fixture(scope="session")
def example_metadata_csv_df(example_csv_metadata_file_path):
    return pd.read_csv(example_csv_metadata_file_path, skiprows=1)


@pytest.fixture(scope="session")
def fixed_seed_random_generator() -> Generator:
    """
    Provides a NumPy random number generator with a fixed seed (42) to ensure reproducibility across tests.
    """
    return np.random.default_rng(seed=42)


# ======= Non-array data =======


@pytest.fixture(scope="session")
def example_int_value() -> int:
    """
    Provides a sample integer value for basic test cases.
    """
    return 1234


@pytest.fixture(scope="session")
def example_float_value() -> float:
    """
    Provides a sample float value for basic test cases.
    """
    return 43.21


@pytest.fixture(scope="session")
def example_string_value() -> float:
    """
    Provides a sample string value for basic test cases.
    """
    return "example value"


# ======= 1D data as numpy arrays =======


@pytest.fixture(scope="session")
def example_int_1d_array(fixed_seed_random_generator) -> np.typing.NDArray:
    """
    Provides a 1D NumPy array of integers (length 10) with values from 0 to 255.
    """
    return fixed_seed_random_generator.integers(0, 256, 10)


@pytest.fixture(scope="session")
def example_float_1d_array(fixed_seed_random_generator) -> np.typing.NDArray:
    """
    Provides a 1D NumPy array of floats (length 10) with values in [0, 1).
    """
    return fixed_seed_random_generator.random(10)


@pytest.fixture(scope="session")
def example_string_1d_array() -> np.typing.NDArray:
    """
    Provides a 1D NumPy array of sample string values.
    """
    return np.array(["a", "b", "c", "d", "e"])


@pytest.fixture(scope="session")
def example_float_1d_array_with_nan(example_float_1d_array) -> np.typing.NDArray:
    """
    Provides a copy of a float 1D NumPy array with NaNs injected at the start, middle, and end.
    Useful for testing NaN-safe operations.
    """
    float_1d_array_with_nan = example_float_1d_array.copy()
    float_1d_array_with_nan[0] = np.nan
    float_1d_array_with_nan[len(float_1d_array_with_nan) // 2] = np.nan
    float_1d_array_with_nan[-1] = np.nan
    return float_1d_array_with_nan


# ======= 2D data as numpy arrays =======


@pytest.fixture(scope="session")
def example_int_2d_array(fixed_seed_random_generator) -> np.typing.NDArray:
    """
    Provides a 10x10 NumPy array of random integers in [0, 256).
    """
    return fixed_seed_random_generator.integers(0, 256, (10, 10))


@pytest.fixture(scope="session")
def example_float_2d_array(fixed_seed_random_generator) -> np.typing.NDArray:
    """
    Provides a 10x10 NumPy array of random floats in [0, 1).
    """
    return fixed_seed_random_generator.random((10, 10))


@pytest.fixture(scope="session")
def example_string_2d_array() -> np.typing.NDArray:
    """
    Provides a 2D NumPy array (4x5) of sample strings.
    """
    return np.array(
        [["a", "b", "c", "d", "e"], ["f", "g", "h", "i", "j"], ["k", "l", "m", "n", "o"], ["p", "q", "r", "s", "t"]]
    )


@pytest.fixture(scope="session")
def example_float_2d_array_with_nan(example_float_2d_array) -> np.typing.NDArray:
    """
    Provides a copy of a float 2D NumPy array with NaNs injected at the top-left, center, and bottom-right.
    Useful for testing NaN handling in 2D data.
    """
    float_2d_array_with_nan = example_float_2d_array.copy()
    float_2d_array_with_nan[(0, 0)] = np.nan
    float_2d_array_with_nan[(len(float_2d_array_with_nan) // 2, len(float_2d_array_with_nan) // 2)] = np.nan
    float_2d_array_with_nan[(-1, -1)] = np.nan
    return float_2d_array_with_nan


# ======= 1D data as python list =======


@pytest.fixture(scope="session")
def example_int_1d_list() -> List[int]:
    """
    Provides a 1D list of 10 random integers in [0, 255] with fixed seed.
    """
    random.seed(42)
    return [random.randint(0, 255) for _ in range(10)]


@pytest.fixture(scope="session")
def example_float_1d_list() -> List[float]:
    """
    Provides a 1D list of 10 random float values in [0, 1) with fixed seed.
    """
    random.seed(42)
    return [random.random() for _ in range(10)]


@pytest.fixture(scope="session")
def example_string_1d_list() -> List[str]:
    """
    Provides a 1D list of sample string values.
    """
    return ["a", "b", "c", "d", "e"]


@pytest.fixture(scope="session")
def example_int_1d_list_with_none(example_int_1d_list) -> List[Union[int, None]]:
    """
    Provides a copy of the int list with None values at the start, middle, and end.
    """
    int_1d_list_with_none = example_int_1d_list.copy()
    int_1d_list_with_none[0] = None
    int_1d_list_with_none[len(int_1d_list_with_none) // 2] = None
    int_1d_list_with_none[-1] = None
    return int_1d_list_with_none


@pytest.fixture(scope="session")
def example_float_1d_list_with_none(example_float_1d_list) -> List[Union[float, None]]:
    """
    Provides a copy of the float list with None values at the start, middle, and end.
    """
    float_1d_list_with_none = example_float_1d_list.copy()
    float_1d_list_with_none[0] = None
    float_1d_list_with_none[len(float_1d_list_with_none) // 2] = None
    float_1d_list_with_none[-1] = None
    return float_1d_list_with_none


@pytest.fixture(scope="session")
def example_string_1d_list_with_none(example_string_1d_list) -> List[Union[str, None]]:
    """
    Provides a copy of the string list with None values at the start, middle, and end.
    """
    string_1d_list_with_none = example_string_1d_list.copy()
    string_1d_list_with_none[0] = None
    string_1d_list_with_none[len(string_1d_list_with_none) // 2] = None
    string_1d_list_with_none[-1] = None
    return string_1d_list_with_none


# ======= 2D data as python list =======


@pytest.fixture(scope="session")
def example_int_2d_list() -> List[List[int]]:
    """
    Provides a 2D list (10x10) of random integers in [0, 255] with fixed seed.
    """
    random.seed(42)
    return [[random.randint(0, 255) for _ in range(10)] for _ in range(10)]


@pytest.fixture(scope="session")
def example_float_2d_list() -> List[List[float]]:
    """
    Provides a 2D list (10x10) of random float values in [0, 1) with fixed seed.
    """
    random.seed(42)
    return [[random.random() for _ in range(10)] for _ in range(10)]


@pytest.fixture(scope="session")
def example_string_2d_list() -> List[List[str]]:
    """
    Provides a 2D list of sample string values (4x5 grid).
    """
    return [["a", "b", "c", "d", "e"], ["f", "g", "h", "i", "j"], ["k", "l", "m", "n", "o"], ["p", "q", "r", "s", "t"]]


@pytest.fixture(scope="session")
def example_int_2d_list_with_none(example_int_2d_list) -> List[List[Union[int, None]]]:
    """
    Provides a copy of the 2D int list with None values injected at the top-left, center, and bottom-right.
    """
    int_2d_list_with_none = example_int_2d_list.copy()
    int_2d_list_with_none[0][0] = None
    int_2d_list_with_none[len(int_2d_list_with_none) // 2][len(int_2d_list_with_none) // 2] = None
    int_2d_list_with_none[-1][-1] = None
    return int_2d_list_with_none


@pytest.fixture(scope="session")
def example_float_2d_list_with_none(example_float_2d_list) -> List[List[Union[float, None]]]:
    """
    Provides a copy of the 2D float list with None values injected at the top-left, center, and bottom-right.
    """
    float_2d_list_with_none = example_float_2d_list.copy()
    float_2d_list_with_none[0][0] = None
    float_2d_list_with_none[len(example_float_2d_list) // 2][len(example_float_2d_list) // 2] = None
    float_2d_list_with_none[-1][-1] = None
    return float_2d_list_with_none


@pytest.fixture(scope="session")
def example_string_2d_list_with_none(example_string_2d_list) -> List[List[Union[str, None]]]:
    """
    Provides a copy of the 2D string list with None values injected at the top-left, center, and bottom-right.
    """
    string_2d_list_with_none = example_string_2d_list.copy()
    string_2d_list_with_none[0][0] = None
    string_2d_list_with_none[len(string_2d_list_with_none) // 2][len(string_2d_list_with_none) // 2] = None
    string_2d_list_with_none[-1][-1] = None
    return string_2d_list_with_none


# ======= Additional metadata =======


@pytest.fixture(scope="session")
def example_metadata(fixed_seed_random_generator) -> Dict[str, Any]:
    """
    Provides a sample metadata dictionary with mixed types, including NumPy arrays.
    Useful for testing metadata compatibility and serialization.
    """
    return {
        "str metadata": "I'm a string metadata",
        "float metadata": 1.5,
        "int metadata": 42,
        "list metadata": [1, 2, 3, 4, 5],
        "numpy array metadata": fixed_seed_random_generator.integers(0, 10, 5),
    }


@pytest.fixture(scope="session")
def example_unit() -> str:
    """
    Provides a sample unit string representing a measurement unit.
    """
    return "Some measurement unit"


# ======= Assonant Entries =======


@pytest.fixture(scope="function")
def example_entry() -> Entry:
    """
    Provides a mocked Assonant entry for the CARNAUBA beamline with a fixed name.
    """
    return AssonantEntryFactory.create_entry(beamline_name=BeamlineName.CARNAUBA, entry_name="entry")


# ======= Assonant DataHandlers =======


# DataField
@pytest.fixture(scope="function")
def example_none_data_field() -> DataField:
    """
    Provides a mocked data field with all values set to None.
    """
    return AssonantDataHandlerFactory.create_data_field(value=None, unit=None, extra_metadata=None)


@pytest.fixture(scope="function")
def example_int_1d_array_data_field(example_int_1d_array, example_unit, example_metadata) -> DataField:
    """
    Provides a mocked data field using a 1D integer array and metadata.
    """
    return AssonantDataHandlerFactory.create_data_field(
        value=example_int_1d_array, unit=example_unit, extra_metadata=example_metadata
    )


@pytest.fixture(scope="function")
def example_float_2d_array_data_field(example_float_2d_array, example_unit, example_metadata) -> DataField:
    """
    Provides a mocked data field using a 2D float array and metadata.
    """
    return AssonantDataHandlerFactory.create_data_field(
        value=example_float_2d_array, unit=example_unit, extra_metadata=example_metadata
    )


@pytest.fixture(scope="function")
def example_string_data_field(example_string_1d_array, example_unit, example_metadata) -> DataField:
    """
    Provides a mocked data field using a 1D string array and metadata.
    """
    return AssonantDataHandlerFactory.create_data_field(
        value=example_string_1d_array, unit=example_unit, extra_metadata=example_metadata
    )


# Axis
@pytest.fixture(scope="function")
def example_translation_axis(example_float_1d_array, example_unit, example_metadata) -> Axis:
    """
    Provides a mocked translation axis using a 1D float array and metadata.
    """
    return AssonantDataHandlerFactory.create_axis(
        transformation_type=TransformationType.TRANSLATION,
        value=example_float_1d_array,
        unit=example_unit,
        extra_metadata=example_metadata,
    )


@pytest.fixture(scope="function")
def example_rotation_axis(example_float_1d_array, example_unit, example_metadata) -> Axis:
    """
    Provides a mocked rotation axis using a 1D float array and metadata.
    """
    return AssonantDataHandlerFactory.create_axis(
        transformation_type=TransformationType.ROTATION,
        value=example_float_1d_array,
        unit=example_unit,
        extra_metadata=example_metadata,
    )


@pytest.fixture(scope="function")
def example_none_axis() -> Axis:
    """
    Provides a mocked rotation axis using a 1D float array and metadata.
    """
    return AssonantDataHandlerFactory.create_axis(
        transformation_type=TransformationType.ROTATION,
        value=None,
        unit=None,
        extra_metadata=None,
    )


# TimeSeries
@pytest.fixture(scope="function")
def example_int_1d_timeseries_data_field(
    example_float_1d_array, example_int_1d_array, example_unit, example_metadata
) -> TimeSeries:
    """
    Provides a mocked timeseries data field using a 1D float array and integer timestamps.
    """
    return AssonantDataHandlerFactory.create_timeseries_field(
        value=example_float_1d_array,
        timestamps=example_int_1d_array,
        unit=example_unit,
        extra_metadata=example_metadata,
        timestamps_unit=example_unit,
        timestamp_extra_metadata=example_metadata,
    )


@pytest.fixture(scope="function")
def example_float_2d_timeseries_data_field(
    example_float_2d_array, example_int_1d_array, example_unit, example_metadata
) -> TimeSeries:
    """
    Provides a mocked timeseries data field using a 2D float array and integer timestamps.
    """
    return AssonantDataHandlerFactory.create_timeseries_field(
        value=example_float_2d_array,
        timestamps=example_int_1d_array,
        unit=example_unit,
        extra_metadata=example_metadata,
        timestamps_unit=example_unit,
        timestamp_extra_metadata=example_metadata,
    )


@pytest.fixture(scope="function")
def example_none_timeseries_data_field() -> TimeSeries:
    """
    Provides a mocked timeseries data field using a 1D float array and integer timestamps.
    """
    return AssonantDataHandlerFactory.create_timeseries_field(
        value=None,
        timestamps=None,
        unit=None,
        extra_metadata=None,
        timestamps_unit=None,
        timestamp_extra_metadata=None,
    )


@pytest.fixture(scope="function")
def example_timeseries_translation_axis(
    example_float_1d_array, example_int_1d_array, example_unit, example_metadata
) -> Axis:
    """
    Provides a mocked timeseries translation axis using 1D float values and integer timestamps.
    """
    return AssonantDataHandlerFactory.create_timeseries_axis(
        transformation_type=TransformationType.TRANSLATION,
        value=example_float_1d_array,
        timestamps=example_int_1d_array,
        unit=example_unit,
        extra_metadata=example_metadata,
        timestamps_unit=example_unit,
        timestamp_extra_metadata=example_metadata,
    )


@pytest.fixture(scope="function")
def example_timeseries_rotation_axis(
    example_float_2d_array, example_int_1d_array, example_unit, example_metadata
) -> Axis:
    """
    Provides a mocked timeseries rotation axis using 2D float values and integer timestamps.
    """
    return AssonantDataHandlerFactory.create_timeseries_axis(
        transformation_type=TransformationType.ROTATION,
        value=example_float_2d_array,
        timestamps=example_int_1d_array,
        unit=example_unit,
        extra_metadata=example_metadata,
        timestamps_unit=example_unit,
        timestamp_extra_metadata=example_metadata,
    )


# ======= Assonant Components and Subcomponents =======


@pytest.fixture(scope="function")
def example_base_component() -> Component:
    """
    Provides a mocked base component named 'main_component' using the generic Component class.
    """
    return AssonantComponentFactory.create_component_by_class_type(Component, "main_component")


@pytest.fixture(scope="function")
def example_subcomponent() -> Component:
    """
    Provides an example subcomponent using the generic Component class.
    """
    return AssonantComponentFactory.create_component_by_class_type(Component, "subcomponent")


@pytest.fixture(scope="function")
def example_components_collection() -> Dict[str, Component]:
    """
    Provides an example subcomponent using the generic Component class.
    """

    component_collection = {}

    for name, _ in inspect.getmembers(importlib.import_module("assonant.data_classes.components"), inspect.isclass):
        component_collection[name] = AssonantComponentFactory.create_component_by_class_name(name, name.lower())

    return component_collection


@pytest.fixture(scope="session")
def component_to_nexus_mapping() -> Dict[Component, Union[NXgroup, NXfield, NXroot]]:
    """
    Provides a dict that maps the Assonant Component to its respective NeXus object.
    """
    component_to_nexus_class_map = {
        Wiggler: NXinsertion_device,
        Undulator: NXinsertion_device,
        BendingMagnet: NXbending_magnet,
        Grating: NXgrating,
        Sensor: NXsensor,
        Detector: NXdetector,
        Monochromator: NXmonochromator,
        Mirror: NXmirror,
        Shutter: NXbeam_stop,
        Slit: NXslit,
        Collimator: NXcollimator,
        StorageRing: NXsource,
        Sample: NXsample,
        Entry: NXentry,
        BeamStopper: NXbeam_stop,
        MonochromatorCrystal: NXcrystal,
        MonochromatorVelocitySelector: NXvelocity_selector,
        BVS: NXdetector,
        Beamline: NXinstrument,
        Beam: NXbeam,
        Pinhole: NXpinhole,
        FresnelZonePlate: NXfresnel_zone_plate,
        DetectorROI: NXgroup,  # This is a contributed definition so current bypassed as NXgroup
        DetectorChannel: NXdetector_channel,
        DetectorModule: NXdetector_module,
        Cryojet: NXgroup,  # This is a custom group created so current bypassed as NXgroup
        GraniteBase: NXgroup,  # This is a custom group created so current bypassed as NXgroup
        Dewar: NXgroup,  # This is a custom group created so current bypassed as NXgroup
        Attenuator: NXattenuator,
        Entry: NXentry,
    }

    return component_to_nexus_class_map


@pytest.fixture(scope="session")
def data_handler_to_nexus_mapping() -> Dict[DataHandler, Union[NXgroup, NXfield]]:
    """
    Provides a dict that maps the Assonant DataHandler to its respective NeXus object.
    """
    data_handler_to_nexus_class_map = {DataField: NXfield, Axis: [NXfield, NXlog], TimeSeries: NXlog}

    return data_handler_to_nexus_class_map
