import contextlib
from pathlib import Path

import pytest
from datadoc_model.all_optional.model import DatadocMetadata
from datadoc_model.all_optional.model import DataType
from datadoc_model.all_optional.model import Variable

from dapla_metadata.datasets._merge import BUCKET_NAME_MESSAGE
from dapla_metadata.datasets._merge import DATA_PRODUCT_NAME_MESSAGE
from dapla_metadata.datasets._merge import DATASET_SHORT_NAME_MESSAGE
from dapla_metadata.datasets._merge import DATASET_STATE_MESSAGE
from dapla_metadata.datasets._merge import VARIABLE_DATATYPES_MESSAGE
from dapla_metadata.datasets._merge import VARIABLE_ORDER_MESSAGE
from dapla_metadata.datasets._merge import VARIABLE_RENAME_MESSAGE
from dapla_metadata.datasets._merge import VARIABLES_ADDITIONAL_MESSAGE
from dapla_metadata.datasets._merge import VARIABLES_FEWER_MESSAGE
from dapla_metadata.datasets._merge import DatasetConsistencyStatus
from dapla_metadata.datasets._merge import InconsistentDatasetsError
from dapla_metadata.datasets._merge import InconsistentDatasetsWarning
from dapla_metadata.datasets._merge import check_dataset_consistency
from dapla_metadata.datasets._merge import check_ready_to_merge
from dapla_metadata.datasets._merge import check_variables_consistency
from tests.datasets.constants import TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH
from tests.datasets.constants import VARIABLE_DATA_TYPES
from tests.datasets.constants import VARIABLE_SHORT_NAMES


@pytest.mark.parametrize(
    ("new_dataset_path", "existing_dataset_path"),
    [
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace("v1", "v2"),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace("p2021", "p2022"),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace(
                "/ifpn",
                "/deeper/folder/structure/ifpn",
            ),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
    ],
    ids=[
        "identical path",
        "differing version",
        "differing period",
        "different folder structure",
    ],
)
def test_check_dataset_consistency_consistent_paths(
    new_dataset_path: str,
    existing_dataset_path: str,
):
    result = check_dataset_consistency(
        Path(new_dataset_path),
        Path(existing_dataset_path),
    )
    for r in result:
        assert r.success, f"'{r.message}' failed"


@pytest.mark.parametrize(
    ("new_dataset_path", "existing_dataset_path"),
    [
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace("produkt", "delt"),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace("ifpn", "blah"),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace(
                "klargjorte_data",
                "utdata",
            ),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace(
                "person_testdata",
                "totally_different_dataset",
            ),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
    ],
    ids=["bucket name", "data product name", "dataset state", "dataset short name"],
)
def test_check_dataset_consistency_inconsistent_paths(
    new_dataset_path: str, existing_dataset_path: str, request
):
    result = check_dataset_consistency(
        Path(new_dataset_path),
        Path(existing_dataset_path),
    )
    test_id = request.node.callspec.id
    result_entry = next(r for r in result if r.message.lower() == test_id)  # type: ignore[attr-defined]
    assert not result_entry.success


@pytest.mark.parametrize(
    ("dataset_consistency_status"),
    [
        [
            DatasetConsistencyStatus(
                message=BUCKET_NAME_MESSAGE,
                success=False,
            ),
            DatasetConsistencyStatus(
                message=DATA_PRODUCT_NAME_MESSAGE,
                success=True,
            ),
            DatasetConsistencyStatus(
                message=DATASET_STATE_MESSAGE,
                success=True,
            ),
            DatasetConsistencyStatus(
                message=DATASET_SHORT_NAME_MESSAGE,
                success=True,
            ),
        ],
    ],
)
@pytest.mark.parametrize(
    "errors_as_warnings",
    [True, False],
    ids=["warnings", "errors"],
)
def test_check_ready_to_merge_errors_as_warnings(
    dataset_consistency_status: list[DatasetConsistencyStatus],
    errors_as_warnings: bool,
):
    with contextlib.ExitStack() as stack:
        if errors_as_warnings:
            stack.enter_context(pytest.warns(InconsistentDatasetsWarning))
        else:
            stack.enter_context(pytest.raises(InconsistentDatasetsError))
        check_ready_to_merge(
            dataset_consistency_status,
            errors_as_warnings=errors_as_warnings,
        )


def test_check_dataset_consistency_inconsistent_variable_data_types():
    def create_variables(data_types):
        return [
            Variable(short_name=name, data_type=data_type)
            for name, data_type in zip(VARIABLE_SHORT_NAMES, data_types, strict=False)
        ]

    metadata1 = DatadocMetadata(
        variables=create_variables([*VARIABLE_DATA_TYPES[:-1], DataType.BOOLEAN])
    )
    metadata2 = DatadocMetadata(variables=create_variables(VARIABLE_DATA_TYPES))
    result = check_variables_consistency(
        metadata1.variables,
        metadata2.variables,
    )
    for r in result:
        if VARIABLE_DATATYPES_MESSAGE in r.message:
            assert not r.success, f"'{r.message}' passed but should have failed"
        else:
            assert r.success, f"'{r.message}' failed but should have passed"


@pytest.mark.parametrize(
    ("extracted_variable_names", "existing_variable_names", "expected_message"),
    [
        (
            VARIABLE_SHORT_NAMES,
            VARIABLE_SHORT_NAMES[:-2],
            VARIABLES_ADDITIONAL_MESSAGE,
        ),
        (
            VARIABLE_SHORT_NAMES[:-2],
            VARIABLE_SHORT_NAMES,
            VARIABLES_FEWER_MESSAGE,
        ),
        (
            VARIABLE_SHORT_NAMES,
            [*VARIABLE_SHORT_NAMES[:-1], "blah"],
            VARIABLE_RENAME_MESSAGE,
        ),
        (
            sorted(VARIABLE_SHORT_NAMES),
            VARIABLE_SHORT_NAMES,
            VARIABLE_ORDER_MESSAGE,
        ),
        (
            VARIABLE_SHORT_NAMES,
            VARIABLE_SHORT_NAMES,
            None,
        ),
    ],
    ids=[
        "additional extracted",
        "fewer extracted",
        "renamed",
        "order changed",
        "identical",
    ],
)
def test_check_variables_consistency(
    extracted_variable_names: list[str],
    existing_variable_names: list[str],
    expected_message: str | None,
):
    results = check_variables_consistency(
        [Variable(short_name=name) for name in extracted_variable_names],
        [Variable(short_name=name) for name in existing_variable_names],
    )
    if expected_message:
        for r in results:
            if expected_message in r.message:
                assert not r.success, f"'{r.message}' passed but should have failed"
            else:
                assert r.success, f"'{r.message}' failed but should have passed"
    else:
        assert all(r.success for r in results)
