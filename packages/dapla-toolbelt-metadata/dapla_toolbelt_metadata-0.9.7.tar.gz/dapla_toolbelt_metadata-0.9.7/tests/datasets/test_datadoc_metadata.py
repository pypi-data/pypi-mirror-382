"""Tests for the DataDocMetadata class."""

from __future__ import annotations

import json
import pathlib
import shutil
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID

import arrow
import pytest
from datadoc_model.all_optional.model import Assessment
from datadoc_model.all_optional.model import DatadocMetadata
from datadoc_model.all_optional.model import Dataset
from datadoc_model.all_optional.model import DataSetState
from datadoc_model.all_optional.model import DataSetStatus
from datadoc_model.all_optional.model import DataType
from datadoc_model.all_optional.model import Variable
from datadoc_model.all_optional.model import VariableRole
from pydantic import ValidationError

from dapla_metadata.dapla.user_info import TestUserInfo
from dapla_metadata.datasets.core import Datadoc
from dapla_metadata.datasets.statistic_subject_mapping import StatisticSubjectMapping
from dapla_metadata.datasets.utility.constants import (
    DATASET_FIELDS_FROM_EXISTING_METADATA,
)
from tests.datasets.constants import DATADOC_METADATA_MODULE_CORE
from tests.datasets.constants import TEST_DATASETS_DIRECTORY
from tests.datasets.constants import TEST_EXISTING_METADATA_DIRECTORY
from tests.datasets.constants import TEST_EXISTING_METADATA_FILE_NAME
from tests.datasets.constants import TEST_EXISTING_METADATA_NAMING_STANDARD_FILEPATH
from tests.datasets.constants import TEST_EXISTING_METADATA_WITH_VALID_ID_DIRECTORY
from tests.datasets.constants import TEST_NAMING_STANDARD_COMPATIBLE_DATASET
from tests.datasets.constants import TEST_PARQUET_FILEPATH
from tests.datasets.constants import TEST_PROCESSED_DATA_POPULATION_DIRECTORY
from tests.datasets.constants import TEST_RESOURCES_DIRECTORY

if TYPE_CHECKING:
    from collections.abc import Generator
    from datetime import datetime


@pytest.fixture
def generate_periodic_file(
    existing_data_path: Path,
    insert_string: str,
) -> Generator[Path, None, None]:
    file_name = existing_data_path.name
    insert_pos = file_name.find("_v1")
    new_file_name = file_name[:insert_pos] + insert_string + file_name[insert_pos:]
    new_path = TEST_RESOURCES_DIRECTORY / new_file_name
    shutil.copy(existing_data_path, new_path)
    yield new_path
    if new_path.exists():
        new_path.unlink()


@pytest.mark.usefixtures("existing_metadata_file")
def test_existing_metadata_file(
    metadata: Datadoc,
):
    root = getattr(metadata.dataset.name, "root", [])
    if root:
        assert root[0].languageText == "successfully_read_existing_file"
    else:
        msg = "Root is none"
        raise AssertionError(msg)


def test_metadata_document_percent_complete(metadata: Datadoc):
    dataset = Dataset(dataset_state=DataSetState.OUTPUT_DATA)
    variable_1 = Variable(data_type=DataType.BOOLEAN)
    variable_2 = Variable(data_type=DataType.INTEGER)
    document = DatadocMetadata(
        percentage_complete=0,
        dataset=dataset,
        variables=[variable_1, variable_2],
    )
    metadata.dataset = document.dataset  # type: ignore [assignment]
    metadata.variables = document.variables  # type: ignore [assignment]

    assert metadata.percent_complete == 13


def test_write_metadata_document(
    dummy_timestamp: datetime,
    metadata: Datadoc,
    tmp_path: pathlib.Path,
):
    metadata.dataset.metadata_created_date = dummy_timestamp
    metadata.write_metadata_document()
    written_document = tmp_path / TEST_EXISTING_METADATA_FILE_NAME
    assert Path.exists(written_document)
    assert metadata.dataset.metadata_created_date == dummy_timestamp
    assert (
        metadata.dataset.metadata_created_by == TestUserInfo.PLACEHOLDER_EMAIL_ADDRESS
    )
    assert metadata.dataset.metadata_last_updated_date == dummy_timestamp
    assert (
        metadata.dataset.metadata_last_updated_by
        == TestUserInfo.PLACEHOLDER_EMAIL_ADDRESS
    )

    with Path.open(written_document) as f:
        written_metadata = json.loads(f.read())
        datadoc_metadata = written_metadata["datadoc"]["dataset"]

    assert (
        # Use our pydantic model to read in the datetime string so we get the correct format
        Dataset(
            metadata_created_date=datadoc_metadata["metadata_created_date"],
        ).metadata_created_date
        == dummy_timestamp
    )
    assert (
        datadoc_metadata["metadata_created_by"]
        == TestUserInfo.PLACEHOLDER_EMAIL_ADDRESS
    )
    assert (
        # Use our pydantic model to read in the datetime string so we get the correct format
        Dataset(
            metadata_last_updated_date=datadoc_metadata["metadata_last_updated_date"],
        ).metadata_last_updated_date
        == dummy_timestamp
    )
    assert (
        datadoc_metadata["metadata_last_updated_by"]
        == TestUserInfo.PLACEHOLDER_EMAIL_ADDRESS
    )


@pytest.mark.usefixtures("existing_metadata_file")
@patch(
    DATADOC_METADATA_MODULE_CORE + ".user_info.get_user_info_for_current_platform",
    return_value=TestUserInfo(),
)
def test_write_metadata_document_existing_document(
    _mock_user_info: MagicMock,  # noqa: PT019 it's a patch, not a fixture
    dummy_timestamp: datetime,
    metadata: Datadoc,
):
    original_created_date = metadata.dataset.metadata_created_date
    original_created_by = metadata.dataset.metadata_created_by
    metadata.write_metadata_document()
    assert metadata.dataset.metadata_created_by == original_created_by
    assert metadata.dataset.metadata_created_date == original_created_date
    assert (
        metadata.dataset.metadata_last_updated_by
        == TestUserInfo.PLACEHOLDER_EMAIL_ADDRESS
    )
    assert metadata.dataset.metadata_last_updated_date == dummy_timestamp


def test_metadata_id(metadata: Datadoc):
    assert isinstance(metadata.dataset.id, UUID)


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_EXISTING_METADATA_DIRECTORY / "invalid_id_field"],
)
def test_existing_metadata_none_id(
    existing_metadata_file: Path,
    metadata: Datadoc,
):
    with existing_metadata_file.open() as f:
        pre_open_id: None = json.load(f)["datadoc"]["dataset"]["id"]
    assert pre_open_id is None
    assert isinstance(metadata.dataset.id, UUID)
    metadata.write_metadata_document()
    with existing_metadata_file.open() as f:
        post_write_id = json.load(f)["datadoc"]["dataset"]["id"]
    assert post_write_id == str(metadata.dataset.id)


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_EXISTING_METADATA_DIRECTORY / "valid_id_field"],
)
def test_existing_metadata_valid_id(
    existing_metadata_file: Path,
    metadata: Datadoc,
):
    pre_open_id = ""
    post_write_id = ""
    with existing_metadata_file.open() as f:
        pre_open_id = json.load(f)["datadoc"]["dataset"]["id"]
    assert pre_open_id is not None
    assert isinstance(metadata.dataset.id, UUID)
    assert str(metadata.dataset.id) == pre_open_id
    metadata.write_metadata_document()
    with existing_metadata_file.open() as f:
        post_write_id = json.load(f)["datadoc"]["dataset"]["id"]
    assert post_write_id == pre_open_id


@pytest.mark.parametrize(
    "metadata_document",
    [TEST_EXISTING_METADATA_WITH_VALID_ID_DIRECTORY / TEST_EXISTING_METADATA_FILE_NAME],
)
@pytest.mark.usefixtures("_mock_timestamp", "_mock_user_info")
def test_validate_required_fields_incomplete_metadata(
    metadata_document: Path,
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
):
    with pytest.raises(ValidationError):
        Datadoc(
            metadata_document_path=str(metadata_document),
            statistic_subject_mapping=subject_mapping_fake_statistical_structure,
            validate_required_fields_on_existing_metadata=True,
        )


@pytest.mark.parametrize(
    "metadata_document",
    [TEST_EXISTING_METADATA_NAMING_STANDARD_FILEPATH],
)
@pytest.mark.usefixtures("_mock_timestamp", "_mock_user_info")
def test_validate_required_fields_complete_metadata(
    metadata_document: Path,
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
):
    Datadoc(
        metadata_document_path=str(metadata_document),
        statistic_subject_mapping=subject_mapping_fake_statistical_structure,
        validate_required_fields_on_existing_metadata=True,
    )


def test_dataset_short_name(metadata: Datadoc):
    assert metadata.dataset.short_name == "person_data"


def test_dataset_file_path(metadata: Datadoc):
    assert metadata.dataset.file_path == str(metadata.dataset_path)


def test_variable_role_default_value(metadata: Datadoc):
    assert all(
        v.variable_role == VariableRole.MEASURE.value for v in metadata.variables
    )


def test_is_personal_data_value(metadata: Datadoc):
    assert all(not v.is_personal_data for v in metadata.variables)


def test_save_file_path_metadata_field(
    existing_metadata_file: Path,
    metadata: Datadoc,
):
    metadata.write_metadata_document()
    with existing_metadata_file.open() as f:
        saved_file_path = json.load(f)["datadoc"]["dataset"]["file_path"]
    assert saved_file_path == str(metadata.dataset_path)


def test_save_file_path_dataset_and_no_metadata(
    metadata: Datadoc,
    tmp_path: pathlib.Path,
):
    metadata.write_metadata_document()
    with (tmp_path / TEST_EXISTING_METADATA_FILE_NAME).open() as f:
        saved_file_path = json.load(f)["datadoc"]["dataset"]["file_path"]
    assert saved_file_path == str(metadata.dataset_path)


@pytest.mark.parametrize(
    ("insert_string", "expected_from", "expected_until"),
    [
        ("_p2021", arrow.get("2021-01-01").date(), arrow.get("2021-12-31").date()),
        (
            "_p2022_p2023",
            arrow.get("2022-01-01").date(),
            arrow.get("2023-12-31").date(),
        ),
    ],
)
def test_period_metadata_fields_saved(
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    generate_periodic_file,
    expected_from,
    expected_until,
):
    metadata = Datadoc(
        str(generate_periodic_file),
        statistic_subject_mapping=subject_mapping_fake_statistical_structure,
    )
    assert metadata.dataset.contains_data_from == expected_from
    assert metadata.dataset.contains_data_until == expected_until


@pytest.mark.parametrize(
    ("dataset_path", "expected_type"),
    [
        (
            TEST_PROCESSED_DATA_POPULATION_DIRECTORY
            / "person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            DataSetStatus.INTERNAL.value,
        ),
        (
            TEST_PARQUET_FILEPATH,
            DataSetStatus.DRAFT.value,
        ),
        (
            "",
            None,
        ),
    ],
)
def test_dataset_status_default_value(
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    dataset_path: str,
    expected_type: DataSetStatus | None,
):
    datadoc_metadata = Datadoc(
        str(dataset_path),
        statistic_subject_mapping=subject_mapping_fake_statistical_structure,
    )
    assert datadoc_metadata.dataset.dataset_status == expected_type


@pytest.mark.parametrize(
    ("path_parts_to_insert", "expected_type"),
    [
        (
            "kildedata",
            Assessment.SENSITIVE.value,
        ),
        (
            "inndata",
            Assessment.PROTECTED.value,
        ),
        (
            "klargjorte_data",
            Assessment.PROTECTED.value,
        ),
        (
            "statistikk",
            Assessment.PROTECTED.value,
        ),
        (
            "utdata",
            Assessment.OPEN.value,
        ),
        (
            "",
            None,
        ),
    ],
)
def test_dataset_assessment_default_value(
    expected_type: Assessment | None,
    copy_dataset_to_path: Path,
    thread_pool_executor,
):
    datadoc_metadata = Datadoc(
        dataset_path=str(copy_dataset_to_path),
        statistic_subject_mapping=StatisticSubjectMapping(
            thread_pool_executor,
            source_url="",
        ),
    )
    assert datadoc_metadata.dataset.assessment == expected_type


@pytest.mark.parametrize(
    ("path_parts_to_insert", "expected_subject_code"),
    [
        (["aa_kortnvan_01", "klargjorte_data"], "aa01"),
        (["ab_kortnvan", "utdata"], "ab00"),
        (["aa_kortnvan_01", "no_dataset_state"], None),
        (["unknown_short_name", "klargjorte_data"], None),
    ],
)
def test_extract_subject_field_value_from_statistic_structure_xml(
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    copy_dataset_to_path: Path,
    expected_subject_code: str,
):
    subject_mapping_fake_statistical_structure.wait_for_external_result()
    metadata = Datadoc(
        str(copy_dataset_to_path),
        statistic_subject_mapping=subject_mapping_fake_statistical_structure,
    )
    assert metadata.dataset.subject_field == expected_subject_code


def test_generate_variables_id(
    metadata: Datadoc,
):
    assert all(isinstance(v.id, UUID) for v in metadata.variables)


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_EXISTING_METADATA_DIRECTORY / "invalid_id_field"],
)
def test_existing_metadata_variables_none_id(
    existing_metadata_file: Path,
    metadata: Datadoc,
):
    with existing_metadata_file.open() as f:
        pre_open_id: list = [v["id"] for v in json.load(f)["datadoc"]["variables"]]
    assert all(i is None for i in pre_open_id)

    assert all(isinstance(v.id, UUID) for v in metadata.variables)

    metadata.write_metadata_document()
    with existing_metadata_file.open() as f:
        post_write_id: list = [v["id"] for v in json.load(f)["datadoc"]["variables"]]

    assert post_write_id == [str(v.id) for v in metadata.variables]


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_EXISTING_METADATA_DIRECTORY / "valid_variable_id_field"],
)
def test_existing_metadata_variables_valid_id(
    existing_metadata_file: Path,
    metadata: Datadoc,
):
    with existing_metadata_file.open() as f:
        pre_open_id: list = [v["id"] for v in json.load(f)["datadoc"]["variables"]]

    assert all(isinstance(v.id, UUID) for v in metadata.variables)
    metadata_variable_ids = [str(v.id) for v in metadata.variables]
    assert metadata_variable_ids == pre_open_id

    metadata.write_metadata_document()
    with existing_metadata_file.open() as f:
        post_write_id: list = [v["id"] for v in json.load(f)["datadoc"]["variables"]]

    assert pre_open_id == post_write_id


@pytest.mark.parametrize(
    ("index", "expected_text"),
    [
        (0, "Norge"),
        (1, "Noreg"),
        (2, "Norway"),
    ],
)
def test_default_spatial_coverage_description(
    metadata: Datadoc,
    index: int,
    expected_text: str,
):
    ls = metadata.dataset.spatial_coverage_description
    assert ls.root[index].languageText == expected_text  # type: ignore[union-attr, index]


def test_open_extracted_and_existing_metadata(metadata_merged: Datadoc, tmp_path: Path):
    assert (
        metadata_merged.metadata_document
        == tmp_path
        / "ifpn/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1__DOC.json"
    )
    assert str(metadata_merged.dataset_path) is not None


def test_open_nonexistent_existing_metadata(existing_data_path: Path):
    with pytest.raises(
        ValueError,
        match="Metadata document does not exist! Provided path:",
    ):
        Datadoc(
            str(existing_data_path),
            str(Datadoc.build_metadata_document_path(existing_data_path)),
        )


def test_merge_extracted_and_existing_dataset_metadata(metadata_merged: Datadoc):
    metadata_extracted = Datadoc(
        dataset_path=str(metadata_merged.dataset_path),
    )
    metadata_existing = Datadoc(
        metadata_document_path=str(TEST_EXISTING_METADATA_NAMING_STANDARD_FILEPATH),
    )

    # Should match extracted metadata from the dataset
    assert metadata_merged.dataset.short_name == metadata_extracted.dataset.short_name
    assert metadata_merged.dataset.assessment == metadata_extracted.dataset.assessment
    assert (
        metadata_merged.dataset.dataset_state
        == metadata_extracted.dataset.dataset_state
    )
    assert metadata_merged.dataset.version == metadata_extracted.dataset.version
    assert metadata_merged.dataset.file_path == metadata_extracted.dataset.file_path
    assert (
        metadata_merged.dataset.metadata_created_by
        == metadata_extracted.dataset.metadata_created_by
    )
    assert (
        metadata_merged.dataset.metadata_last_updated_by
        == metadata_extracted.dataset.metadata_last_updated_by
    )
    assert (
        metadata_merged.dataset.contains_data_from
        == metadata_extracted.dataset.contains_data_from
    )
    assert (
        metadata_merged.dataset.contains_data_until
        == metadata_extracted.dataset.contains_data_until
    )

    # Should match existing metadata
    for field in DATASET_FIELDS_FROM_EXISTING_METADATA:
        assert getattr(metadata_merged.dataset, field) == getattr(
            metadata_existing.dataset,
            field,
        ), f"{field} in merged metadata did not match existing metadata"

    # Special cases
    assert metadata_merged.dataset.id != metadata_existing.dataset.id
    assert metadata_merged.dataset.metadata_created_date is None
    assert metadata_merged.dataset.metadata_last_updated_date is None


def test_merge_variables(tmp_path):
    dataset = tmp_path / "fewer_variables_p2021-12-31_p2021-12-31_v1.parquet"
    existing_document = TEST_EXISTING_METADATA_NAMING_STANDARD_FILEPATH
    dataset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        TEST_DATASETS_DIRECTORY / "fewer_variables_p2021-12-31_p2021-12-31_v1.parquet",
        dataset,
    )
    extracted = Datadoc(
        dataset_path=str(dataset),
    )
    existing = Datadoc(
        metadata_document_path=str(existing_document),
    )
    merged = Datadoc(
        dataset_path=str(dataset),
        metadata_document_path=str(existing_document),
        errors_as_warnings=True,
    )
    assert [v.short_name for v in merged.variables] == [
        v.short_name for v in extracted.variables
    ]
    assert all(v.id is not None for v in merged.variables)
    assert [v.id for v in merged.variables] != [v.id for v in existing.variables]
    assert all(
        v.contains_data_from == merged.dataset.contains_data_from
        for v in merged.variables
    )
    assert all(
        v.contains_data_until == merged.dataset.contains_data_until
        for v in merged.variables
    )


def test_merge_with_fewer_variables_in_existing_metadata(tmp_path):
    target = tmp_path / TEST_NAMING_STANDARD_COMPATIBLE_DATASET
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        TEST_DATASETS_DIRECTORY / TEST_NAMING_STANDARD_COMPATIBLE_DATASET,
        target,
    )
    datadoc = Datadoc(
        str(target),
        str(
            TEST_EXISTING_METADATA_DIRECTORY
            / "fewer_variables_p2020-12-31_p2020-12-31_v1__DOC.json",
        ),
        errors_as_warnings=True,
    )
    assert [v.short_name for v in datadoc.variables] == [
        "fnr",
        "sivilstand",
        "bostedskommune",
        "inntekt",
        "bankinnskudd",
        "dato",
    ]
