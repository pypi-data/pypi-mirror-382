"""Tests for the compatibility package."""

import json
from pathlib import Path

import pytest

from dapla_metadata.datasets.compatibility import is_metadata_in_container_structure
from dapla_metadata.datasets.compatibility import upgrade_metadata
from dapla_metadata.datasets.compatibility._handlers import handle_version_2_2_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_3_3_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_4_0_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_5_0_1
from dapla_metadata.datasets.compatibility._handlers import handle_version_6_0_0
from dapla_metadata.datasets.compatibility._utils import DATADOC_KEY
from dapla_metadata.datasets.compatibility._utils import DATASET_KEY
from dapla_metadata.datasets.compatibility._utils import DOCUMENT_VERSION_KEY
from dapla_metadata.datasets.compatibility._utils import PSEUDONYMIZATION_KEY
from dapla_metadata.datasets.compatibility._utils import VARIABLES_KEY
from dapla_metadata.datasets.compatibility._utils import UnknownModelVersionError
from dapla_metadata.datasets.compatibility._utils import add_container
from dapla_metadata.datasets.compatibility._utils import convert_is_personal_data
from dapla_metadata.datasets.compatibility._utils import copy_pseudonymization_metadata
from dapla_metadata.datasets.core import Datadoc
from tests.datasets.constants import TEST_COMPATIBILITY_DIRECTORY
from tests.datasets.constants import TEST_EXISTING_METADATA_FILE_NAME
from tests.datasets.constants import TEST_PSEUDO_DIRECTORY

BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES = [
    d for d in TEST_COMPATIBILITY_DIRECTORY.iterdir() if d.is_dir()
]

BACKWARDS_COMPATIBLE_VERSION_NAMES = [
    d.stem for d in BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES
]


def test_existing_metadata_current_model_version():
    current_model_version = "6.1.0"
    fresh_metadata = {DATADOC_KEY: {DOCUMENT_VERSION_KEY: current_model_version}}
    upgraded_metadata = upgrade_metadata(fresh_metadata)
    assert upgraded_metadata == fresh_metadata


def test_handle_version_2_2_0() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_COMPATIBILITY_DIRECTORY
        / "v2_2_0"
        / TEST_EXISTING_METADATA_FILE_NAME
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_2_2_0(fresh_metadata)
    assert "custom_type" in upgraded_metadata[DATADOC_KEY][DATASET_KEY]
    assert "custom_type" in upgraded_metadata[DATADOC_KEY][VARIABLES_KEY][0]
    assert "special_value" in upgraded_metadata[DATADOC_KEY][VARIABLES_KEY][0]


def test_handle_version_3_3_0() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_COMPATIBILITY_DIRECTORY
        / "v3_3_0"
        / TEST_EXISTING_METADATA_FILE_NAME
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_3_3_0(fresh_metadata)
    assert (
        "direct_person_identifying"
        not in upgraded_metadata[DATADOC_KEY][VARIABLES_KEY][0]
    )


def test_handle_version_4_0_0() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_PSEUDO_DIRECTORY
        / "dataset_and_pseudo"
        / "v4_0_0_person_data_v1__DOC.json"
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_4_0_0(fresh_metadata)
    pseudo_field = upgraded_metadata[DATADOC_KEY][VARIABLES_KEY][0][
        PSEUDONYMIZATION_KEY
    ]
    assert pseudo_field["encryption_algorithm"] == "TINK-DAEAD"
    assert pseudo_field["encryption_key_reference"] == "ssb-common-key-1"
    assert pseudo_field["pseudonymization_time"] == "2010-09-05"
    assert pseudo_field["encryption_algorithm_parameters"] == [
        {"keyId": "ssb-common-key-1"}
    ]
    assert (
        upgraded_metadata[DATADOC_KEY][VARIABLES_KEY][1][PSEUDONYMIZATION_KEY] is None
    )


def test_handle_version_4_0_0_without_pseudo() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_PSEUDO_DIRECTORY
        / "dataset_and_pseudo"
        / "no_pseudo_v4_0_0_person_data_v1__DOC.json"
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_4_0_0(fresh_metadata)
    assert PSEUDONYMIZATION_KEY not in upgraded_metadata
    assert all(
        PSEUDONYMIZATION_KEY not in v
        for v in upgraded_metadata[DATADOC_KEY][VARIABLES_KEY]
    )


def test_handle_version_5_0_1() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_COMPATIBILITY_DIRECTORY
        / "v5_0_1"
        / TEST_EXISTING_METADATA_FILE_NAME
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_5_0_1(fresh_metadata)
    removed_dataset_fields = [
        "contains_personal_data",
        "unit_type",
        "data_source",
        "temporality_type",
    ]
    for f in removed_dataset_fields:
        assert f not in upgraded_metadata[DATADOC_KEY][DATASET_KEY]
    added_variables_fields = [
        "is_personal_data",
        "unit_type",
        "data_source",
        "temporality_type",
    ]
    for f in added_variables_fields:
        assert all(f in v for v in upgraded_metadata[DATADOC_KEY][VARIABLES_KEY])


def test_handle_version_6_0_0() -> None:
    existing_metadata_file = (
        Path(__file__).resolve().parents[2]
        / TEST_COMPATIBILITY_DIRECTORY
        / "v6_0_0"
        / TEST_EXISTING_METADATA_FILE_NAME
    )
    fresh_metadata = json.loads(existing_metadata_file.read_text(encoding="utf-8"))

    upgraded = handle_version_6_0_0(fresh_metadata)

    dataset = upgraded[DATADOC_KEY][DATASET_KEY]

    assert all(f not in dataset for f in ["use_restriction", "use_restriction_date"])

    assert "use_restrictions" in dataset

    first_use_restriction = dataset["use_restrictions"][0]
    assert first_use_restriction["use_restriction_type"] == "DELETION_ANONYMIZATION"
    assert first_use_restriction["use_restriction_date"] == "2022-09-05"


def test_existing_metadata_unknown_model_version():
    fresh_metadata = {DATADOC_KEY: {DOCUMENT_VERSION_KEY: "0.27.65"}}
    with pytest.raises(UnknownModelVersionError):
        upgrade_metadata(fresh_metadata)


@pytest.mark.parametrize(
    "existing_metadata_path",
    BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES,
    ids=BACKWARDS_COMPATIBLE_VERSION_NAMES,
)
def test_backwards_compatibility(
    existing_metadata_file: Path,
    metadata: Datadoc,
):
    with existing_metadata_file.open() as f:
        file_metadata = json.loads(f.read())

    if is_metadata_in_container_structure(file_metadata):
        file_metadata = file_metadata[DATADOC_KEY]

    # Just test a single value to make sure we have a working model
    assert metadata.dataset.short_name == file_metadata[DATASET_KEY]["short_name"]  # type: ignore [union-attr, index]


def test_add_container():
    doc = {
        "percentage_complete": 98,
        DOCUMENT_VERSION_KEY: "2.1.0",
        DATASET_KEY: {"short_name": "person_data_v1", "assessment": "SENSITIVE"},
    }
    doc_with_container = add_container(doc)
    assert doc_with_container[DOCUMENT_VERSION_KEY] == "0.0.1"
    assert doc_with_container[DATADOC_KEY][DOCUMENT_VERSION_KEY] == "2.1.0"
    assert PSEUDONYMIZATION_KEY in doc_with_container


@pytest.mark.parametrize(
    ("input_value", "expected_result"),
    [
        ("NON_PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA", True),
        ("PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA", True),
        ("NOT_PERSONAL_DATA", False),
        (None, None),
        (False, False),
        (True, True),
    ],
)
def test_convert_is_personal_data(input_value, expected_result):
    supplied_metadata = {
        DATADOC_KEY: {VARIABLES_KEY: [{"is_personal_data": input_value}]}
    }

    convert_is_personal_data(supplied_metadata)

    assert (
        supplied_metadata[DATADOC_KEY][VARIABLES_KEY][0]["is_personal_data"]
        == expected_result
    )


def test_copy_pseudonymization_metadata_shortname_mismatch():
    supplied_metadata = {
        DATADOC_KEY: {VARIABLES_KEY: [{"short_name": "pers_id"}]},
        PSEUDONYMIZATION_KEY: {
            DOCUMENT_VERSION_KEY: "0.1.0",
            "pseudo_dataset": None,
            "pseudo_variables": [
                {
                    "short_name": "fnr",
                    "data_element_path": "fnr",
                    "data_element_pattern": "**/fnr",
                    "stable_identifier_type": None,
                    "stable_identifier_version": None,
                    "encryption_algorithm": "TINK-DAEAD",
                    "encryption_key_reference": "ssb-common-key-1",
                    "encryption_algorithm_parameters": [{"keyId": "ssb-common-key-1"}],
                    "source_variable": None,
                    "source_variable_datatype": None,
                }
            ],
        },
    }

    copy_pseudonymization_metadata(supplied_metadata)

    assert len(supplied_metadata[DATADOC_KEY][VARIABLES_KEY]) == 1
    assert (
        supplied_metadata[DATADOC_KEY][VARIABLES_KEY][0][PSEUDONYMIZATION_KEY] is None
    )
