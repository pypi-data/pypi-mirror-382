"""Tests for pseudonymization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import TYPE_CHECKING

import pytest
from datadoc_model.all_optional.model import Pseudonymization

from dapla_metadata.datasets.utility.constants import DAEAD_ENCRYPTION_KEY_REFERENCE
from dapla_metadata.datasets.utility.constants import ENCRYPTION_PARAMETER_KEY_ID
from dapla_metadata.datasets.utility.constants import ENCRYPTION_PARAMETER_SNAPSHOT_DATE
from dapla_metadata.datasets.utility.constants import ENCRYPTION_PARAMETER_STRATEGY
from dapla_metadata.datasets.utility.constants import ENCRYPTION_PARAMETER_STRATEGY_SKIP
from dapla_metadata.datasets.utility.constants import PAPIS_ENCRYPTION_KEY_REFERENCE
from dapla_metadata.datasets.utility.constants import PAPIS_STABLE_IDENTIFIER_TYPE
from dapla_metadata.datasets.utility.enums import EncryptionAlgorithm
from dapla_metadata.datasets.utility.utils import get_current_date
from tests.datasets.constants import TEST_PSEUDO_DIRECTORY

if TYPE_CHECKING:
    from datetime import datetime  # noqa: TC004
    from pathlib import Path

    from dapla_metadata.datasets.core import Datadoc


@dataclass
class PseudoCase:
    new_pseudo: Pseudonymization | None = None
    expected_algorithm: str | None = None
    expected_stable_type: str | None = None
    expected_key: str | None = None
    expected_params: list[dict] | None = None
    expected_pseudo_time: datetime | None = None
    expected_stable_version: str | None = None


def _assert_dicts_in_list(expected: list[dict] | None, actual: list[dict]):
    if expected:
        for d in expected:
            assert d in actual, f"Missing expected dict: {d}"


@pytest.mark.parametrize(
    "case",
    [
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE},
                {ENCRYPTION_PARAMETER_STRATEGY: ENCRYPTION_PARAMETER_STRATEGY_SKIP},
            ],
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                encryption_key_reference="fall-out-2",
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_key="fall-out-2",
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE},
                {ENCRYPTION_PARAMETER_STRATEGY: ENCRYPTION_PARAMETER_STRATEGY_SKIP},
            ],
        ),
        PseudoCase(
            new_pseudo=None,
            expected_algorithm=None,
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                pseudonymization_time=datetime(
                    2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE},
                {ENCRYPTION_PARAMETER_STRATEGY: ENCRYPTION_PARAMETER_STRATEGY_SKIP},
            ],
            expected_pseudo_time=datetime(2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc),
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                encryption_algorithm_parameters=[{"someKey": "someValue"}],
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"someKey": "someValue"},
                {ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE},
                {ENCRYPTION_PARAMETER_STRATEGY: ENCRYPTION_PARAMETER_STRATEGY_SKIP},
            ],
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                encryption_algorithm_parameters=[
                    {ENCRYPTION_PARAMETER_KEY_ID: "heaven-ref-3"}
                ],
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: "heaven-ref-3"},
                {ENCRYPTION_PARAMETER_STRATEGY: ENCRYPTION_PARAMETER_STRATEGY_SKIP},
            ],
        ),
    ],
    ids=[
        "Add new pseudonymization PAPIS without stable ID",
        "Add new pseudonymization PAPIS without stable ID - encryption key refrence set",
        "No pseudonymization - empty pseudonymization",
        "Add new pseudonymization PAPIS without stable ID - pseudonymization time",
        "Add new pseudonymization PAPIS without stable ID - additional algorithm parameters",
        "Add new pseudonymization PAPIS without stable ID - keyId in algorithm parameters",
    ],
)
def test_add_default_pseudonymization_values_papis_without_stable_id(
    case: PseudoCase, metadata: Datadoc
):
    sykepenger = metadata.variables_lookup["sykepenger"]

    assert sykepenger.short_name is not None

    metadata.add_pseudonymization(sykepenger.short_name, case.new_pseudo)
    assert sykepenger.pseudonymization is not None
    if sykepenger.pseudonymization:
        assert (
            sykepenger.pseudonymization.encryption_algorithm == case.expected_algorithm
        )
        assert sykepenger.pseudonymization.encryption_key_reference == case.expected_key
        assert (
            sykepenger.pseudonymization.pseudonymization_time
            == case.expected_pseudo_time
        )
        if sykepenger.pseudonymization.encryption_algorithm_parameters is None:
            assert case.expected_params is None
        else:
            _assert_dicts_in_list(
                case.expected_params,
                sykepenger.pseudonymization.encryption_algorithm_parameters,
            )


@pytest.mark.parametrize(
    "case",
    [
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE},
                {ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()},
                {ENCRYPTION_PARAMETER_STRATEGY: ENCRYPTION_PARAMETER_STRATEGY_SKIP},
            ],
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
                encryption_key_reference="oh-no-4",
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_key="oh-no-4",
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE},
                {ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()},
                {ENCRYPTION_PARAMETER_STRATEGY: ENCRYPTION_PARAMETER_STRATEGY_SKIP},
            ],
        ),
        PseudoCase(
            new_pseudo=None,
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
                pseudonymization_time=datetime(
                    2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE},
                {ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()},
                {ENCRYPTION_PARAMETER_STRATEGY: ENCRYPTION_PARAMETER_STRATEGY_SKIP},
            ],
            expected_pseudo_time=datetime(2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc),
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
                stable_identifier_version="3012-10-11",
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE},
                {ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()},
                {ENCRYPTION_PARAMETER_STRATEGY: ENCRYPTION_PARAMETER_STRATEGY_SKIP},
            ],
            expected_stable_version="3012-10-11",
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
                encryption_algorithm_parameters=[
                    {ENCRYPTION_PARAMETER_SNAPSHOT_DATE: "2025-12-12"}
                ],
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE},
                {ENCRYPTION_PARAMETER_STRATEGY: ENCRYPTION_PARAMETER_STRATEGY_SKIP},
            ],
        ),
    ],
    ids=[
        "Add new pseudonymization PAPIS with stable ID",
        "Add pseudonymization PAPIS with stable ID - encryption key reference set",
        "No pseudonymization - empty pseudonymization",
        "Add pseudonymization time PAPIS with stable ID - pseudonymization time",
        "Add pseudonymization time PAPIS with stable ID - stable version",
        "Add pseudonymization time PAPIS with stable ID - snapshotDate set",
    ],
)
def test_add_default_pseudonymization_values_papis_with_stable_id(
    case: PseudoCase, metadata: Datadoc
):
    sykepenger = metadata.variables_lookup["sykepenger"]

    assert sykepenger.short_name is not None

    metadata.add_pseudonymization(sykepenger.short_name, case.new_pseudo)
    assert sykepenger.pseudonymization is not None
    assert (
        sykepenger.pseudonymization.stable_identifier_type == case.expected_stable_type
    )
    assert sykepenger.pseudonymization.encryption_algorithm == case.expected_algorithm
    assert sykepenger.pseudonymization.encryption_key_reference == case.expected_key
    assert (
        sykepenger.pseudonymization.stable_identifier_version
        == case.expected_stable_version
    )
    assert (
        sykepenger.pseudonymization.pseudonymization_time == case.expected_pseudo_time
    )
    algorithm_params = sykepenger.pseudonymization.encryption_algorithm_parameters
    if algorithm_params is None:
        assert case.expected_params is None
    else:
        _assert_dicts_in_list(
            case.expected_params,
            algorithm_params,
        )


@pytest.mark.parametrize(
    "case",
    [
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.DAEAD_ENCRYPTION_ALGORITHM.value,
            ),
            expected_algorithm=EncryptionAlgorithm.DAEAD_ENCRYPTION_ALGORITHM.value,
            expected_key=DAEAD_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: DAEAD_ENCRYPTION_KEY_REFERENCE},
            ],
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.DAEAD_ENCRYPTION_ALGORITHM.value,
                encryption_key_reference="jippi-ya",
            ),
            expected_algorithm=EncryptionAlgorithm.DAEAD_ENCRYPTION_ALGORITHM.value,
            expected_key="jippi-ya",
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: DAEAD_ENCRYPTION_KEY_REFERENCE},
            ],
        ),
        PseudoCase(
            new_pseudo=None,
            expected_algorithm=None,
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.DAEAD_ENCRYPTION_ALGORITHM.value,
                pseudonymization_time=datetime(
                    2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            expected_algorithm=EncryptionAlgorithm.DAEAD_ENCRYPTION_ALGORITHM.value,
            expected_key=DAEAD_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: DAEAD_ENCRYPTION_KEY_REFERENCE},
            ],
            expected_pseudo_time=datetime(2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc),
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.DAEAD_ENCRYPTION_ALGORITHM.value,
                encryption_algorithm_parameters=[
                    {ENCRYPTION_PARAMETER_KEY_ID: "not-my-responsibility"}
                ],
            ),
            expected_algorithm=EncryptionAlgorithm.DAEAD_ENCRYPTION_ALGORITHM.value,
            expected_key=DAEAD_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: "not-my-responsibility"},
            ],
            expected_pseudo_time=datetime(2025, 1, 1, 12, 30, 0, tzinfo=timezone.utc),
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.DAEAD_ENCRYPTION_ALGORITHM.value,
                encryption_algorithm_parameters=[{"so-private": "key-hi-hi"}],
            ),
            expected_algorithm=EncryptionAlgorithm.DAEAD_ENCRYPTION_ALGORITHM.value,
            expected_key=DAEAD_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"so-private": "key-hi-hi"},
                {ENCRYPTION_PARAMETER_KEY_ID: DAEAD_ENCRYPTION_KEY_REFERENCE},
            ],
            expected_pseudo_time=datetime(2025, 1, 1, 12, 30, 0, tzinfo=timezone.utc),
        ),
    ],
    ids=[
        "Add new pseudonymization DAED",
        "Add pseudonymization DAED - encryption key refrence set",
        "No pseudonymization - empty pseudonymization",
        "Add pseudonymization DAED - pseudonymization time",
        "Add pseudonymization DAED - keyId in algorithm parameters",
        "Add pseudonymization DAED - additional algorithm parameters",
    ],
)
def test_add_default_pseudonymization_values_daed(case: PseudoCase, metadata: Datadoc):
    sykepenger = metadata.variables_lookup["sykepenger"]

    assert sykepenger.short_name is not None
    metadata.add_pseudonymization(sykepenger.short_name, case.new_pseudo)
    assert sykepenger.pseudonymization is not None

    assert sykepenger.pseudonymization.encryption_algorithm == case.expected_algorithm
    assert sykepenger.pseudonymization.encryption_key_reference == case.expected_key
    assert (
        sykepenger.pseudonymization.stable_identifier_version
        == case.expected_stable_version
    )
    algorithm_params = sykepenger.pseudonymization.encryption_algorithm_parameters
    if algorithm_params is None:
        assert case.expected_params is None
    else:
        _assert_dicts_in_list(
            case.expected_params,
            algorithm_params,
        )


@pytest.mark.parametrize(
    "case",
    [
        PseudoCase(
            new_pseudo=Pseudonymization(
                encryption_algorithm="unknown",
            ),
            expected_algorithm="unknown",
        ),
        PseudoCase(
            new_pseudo=Pseudonymization(
                pseudonymization_time=datetime(
                    2025, 10, 29, 0, 0, 0, tzinfo=timezone.utc
                ),
                encryption_algorithm="unknown",
                encryption_key_reference=DAEAD_ENCRYPTION_KEY_REFERENCE,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
                stable_identifier_version="2-a-3",
                encryption_algorithm_parameters=[
                    {ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE},
                    {"someKey": "specialValue"},
                ],
            ),
            expected_algorithm="unknown",
            expected_key=DAEAD_ENCRYPTION_KEY_REFERENCE,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_params=[
                {ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE},
                {"someKey": "specialValue"},
            ],
            expected_pseudo_time=datetime(2025, 10, 29, 0, 0, 0, tzinfo=timezone.utc),
            expected_stable_version="2-a-3",
        ),
    ],
    ids=[
        "Add new unknown encryption algorithm",
        "Add new unknown encryption algorithm - all values",
    ],
)
def test_add_pseudonymization_unknown_algorithm(case: PseudoCase, metadata: Datadoc):
    sykepenger = metadata.variables_lookup["sykepenger"]
    assert sykepenger.short_name is not None

    metadata.add_pseudonymization(sykepenger.short_name, case.new_pseudo)
    assert sykepenger.pseudonymization is not None

    assert sykepenger.pseudonymization.encryption_algorithm == case.expected_algorithm
    assert sykepenger.pseudonymization.encryption_key_reference == case.expected_key
    assert (
        sykepenger.pseudonymization.stable_identifier_version
        == case.expected_stable_version
    )
    algorithm_params = sykepenger.pseudonymization.encryption_algorithm_parameters
    if algorithm_params is None:
        assert case.expected_params is None
    else:
        _assert_dicts_in_list(
            case.expected_params,
            algorithm_params,
        )


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_add_pseudo_variable(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    test_variable = "sykepenger"
    is_personal_data = metadata.variables_lookup[test_variable].is_personal_data
    metadata.add_pseudonymization(test_variable)
    assert metadata.variables_lookup[test_variable].pseudonymization is not None
    assert metadata.variables_lookup[test_variable].is_personal_data == is_personal_data


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_add_pseudo_variable_non_existent_variable_name(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    with pytest.raises(KeyError):
        metadata.add_pseudonymization("new_pseudo_variable")


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_existing_metadata_file_update_pseudonymization(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    metadata.add_pseudonymization("pers_id")
    variable = metadata.variables_lookup["pers_id"]

    assert variable.pseudonymization is not None
    assert variable.pseudonymization.encryption_algorithm is None
    variable.pseudonymization.encryption_algorithm = "new_encryption_algorithm"
    assert variable.pseudonymization.encryption_algorithm == "new_encryption_algorithm"


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_update_pseudo(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    variable = metadata.variables_lookup["pers_id"]

    pseudo = Pseudonymization(encryption_algorithm="new_encryption_algorithm")

    metadata.add_pseudonymization("pers_id", pseudo)

    assert variable.pseudonymization is not None
    assert variable.pseudonymization.encryption_algorithm == "new_encryption_algorithm"
    assert variable.pseudonymization.encryption_algorithm_parameters is None


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_remove_pseudo_variable(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    test_variable = "alm_inntekt"
    is_personal_data = metadata.variables_lookup[test_variable].is_personal_data
    metadata.remove_pseudonymization(test_variable)
    assert metadata.variables_lookup[test_variable].is_personal_data == is_personal_data
    assert metadata.variables_lookup[test_variable].pseudonymization is None


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_remove_pseudo_variable_non_existent_variable_name(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    with pytest.raises(KeyError):
        metadata.remove_pseudonymization("fnr")
