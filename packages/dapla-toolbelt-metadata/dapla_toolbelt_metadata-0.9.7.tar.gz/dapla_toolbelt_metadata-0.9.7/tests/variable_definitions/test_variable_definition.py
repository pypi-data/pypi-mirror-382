import contextlib
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from dapla_metadata.variable_definitions._generated.vardef_client.models.patch import (
    Patch,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.update_draft import (
    UpdateDraft,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.validity_period import (
    ValidityPeriod,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions._utils._client import VardefClient
from dapla_metadata.variable_definitions._utils.constants import (
    PUBLISHING_BLOCKED_ERROR_MESSAGE,
)
from dapla_metadata.variable_definitions._utils.constants import VARDEF_PROD_URL
from dapla_metadata.variable_definitions._utils.constants import VARDEF_TEST_URL
from dapla_metadata.variable_definitions.exceptions import PublishingBlockedError
from dapla_metadata.variable_definitions.exceptions import VardefFileError
from dapla_metadata.variable_definitions.vardef import Vardef
from dapla_metadata.variable_definitions.variable_definition import (
    IDENTICAL_PATCH_ERROR_MESSAGE,
)
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition
from tests.utils.constants import VARDEF_EXAMPLE_DATE
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID
from tests.variable_definitions.constants import VARIABLE_DEFINITION_EDITING_FILES_DIR
from tests.variable_definitions.test_vardef import PATCH_ID


def test_list_patches():
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.list_patches()[0], VariableDefinition)


def test_get_patch():
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.get_patch(1), VariableDefinition)


def test_list_validity_periods():
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.list_validity_periods()[0], VariableDefinition)


def test_update_draft(
    update_draft: UpdateDraft,
):
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(my_draft.update_draft(update_draft), VariableDefinition)


def test_update_draft_check_model_change(
    update_draft: UpdateDraft,
    mock_update_variable_definition_by_id,
):
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    with patch(
        "dapla_metadata.variable_definitions._generated.vardef_client.api.draft_variable_definitions_api.DraftVariableDefinitionsApi.update_variable_definition_by_id",
        mock_update_variable_definition_by_id,
    ):
        my_draft.update_draft(update_draft=update_draft)
        assert my_draft.classification_reference == "www.newurl.com"
        mock_update_variable_definition_by_id.assert_called_once()


def test_delete_draft():
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert my_draft.id is not None
    result = my_draft.delete_draft()
    assert f"Variable {VARDEF_EXAMPLE_DEFINITION_ID} safely deleted" in result


def test_create_patch(
    patch_fixture: Patch,
    variable_definition: VariableDefinition,
):
    my_variable = variable_definition
    assert my_variable.patch_id == 1
    created_patch = my_variable.create_patch(
        patch=patch_fixture,
        valid_from=VARDEF_EXAMPLE_DATE,
    )
    assert isinstance(
        created_patch,
        VariableDefinition,
    )
    assert created_patch.patch_id == PATCH_ID


def test_create_patch_check_model_change(
    patch_fixture: Patch,
    mock_update_variable_definition_by_id,
):
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    with patch(
        "dapla_metadata.variable_definitions._generated.vardef_client.api.patches_api.PatchesApi.create_patch",
        mock_update_variable_definition_by_id,
    ):
        my_draft.create_patch(patch=patch_fixture)
        assert my_draft.classification_reference == "www.newurl.com"
        mock_update_variable_definition_by_id.assert_called_once()


def test_create_validity_period(
    validity_period: ValidityPeriod,
    variable_definition: VariableDefinition,
):
    my_variable = variable_definition
    assert isinstance(
        my_variable.create_validity_period(validity_period),
        VariableDefinition,
    )


def test_create_validity_period_check_model_change(
    validity_period: ValidityPeriod,
    mock_update_variable_definition_by_id,
):
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    with patch(
        "dapla_metadata.variable_definitions._generated.vardef_client.api.validity_periods_api.ValidityPeriodsApi.create_validity_period",
        mock_update_variable_definition_by_id,
    ):
        my_draft.create_validity_period(validity_period=validity_period)
        assert my_draft.classification_reference == "www.newurl.com"
        mock_update_variable_definition_by_id.assert_called_once()


def test_update_draft_from_file():
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    ).to_file()
    assert my_draft.get_file_path().exists()
    assert isinstance(my_draft.update_draft_from_file(), VariableDefinition)


def test_update_draft_from_file_no_known_file():
    with pytest.raises(FileNotFoundError, match="Could not deduce a path to the file"):
        Vardef.get_variable_definition_by_id(
            VARDEF_EXAMPLE_DEFINITION_ID,
        ).update_draft_from_file()


def test_update_draft_from_file_file_non_existent():
    with pytest.raises(FileNotFoundError):
        Vardef.get_variable_definition_by_id(
            VARDEF_EXAMPLE_DEFINITION_ID,
        ).update_draft_from_file("my_cool_file.yaml")


def test_update_draft_from_file_invalid_yaml(tmp_path: Path):
    invalid = tmp_path / "invalid_yaml.yaml"
    invalid.write_text(
        """--- invalid yaml ---
not allowed:
:why
""",
    )
    with pytest.raises(VardefFileError):
        Vardef.get_variable_definition_by_id(
            VARDEF_EXAMPLE_DEFINITION_ID,
        ).update_draft_from_file(
            invalid,
        )


def test_update_draft_from_file_validation_fails(tmp_path: Path):
    invalid = tmp_path / "fails_validation.yaml"
    invalid.write_text(
        """fails validation""",
    )
    with pytest.raises(ValidationError):
        Vardef.get_variable_definition_by_id(
            VARDEF_EXAMPLE_DEFINITION_ID,
        ).update_draft_from_file(
            invalid,
        )


def test_update_draft_from_file_specify_file():
    assert (
        Vardef.get_variable_definition_by_id(
            VARDEF_EXAMPLE_DEFINITION_ID,
        )
        .update_draft_from_file(
            VARIABLE_DEFINITION_EDITING_FILES_DIR / "classification_reference.yaml",
        )
        .short_name
        == "landbak"
    )


def test_create_patch_from_file(variable_definition: VariableDefinition):
    mock_api_response = MagicMock(name="VariableDefinition")
    mock_api_response.classification_reference = "702"
    with patch.object(
        VariableDefinition,
        "create_patch",
        return_value=mock_api_response,
    ) as mock_create_patch:
        my_patch = variable_definition
        result = my_patch.create_patch_from_file(
            file_path=VARIABLE_DEFINITION_EDITING_FILES_DIR
            / "classification_reference.yaml",
        )

    assert my_patch.classification_reference != result.classification_reference
    mock_create_patch.assert_called_once()


def test_create_patch_change_short_name(variable_definition: VariableDefinition):
    mock_api_response = MagicMock(name="VariableDefinition")
    mock_api_response.classification_reference = "702"
    with (
        patch.object(
            VariableDefinition,
            "create_patch",
            return_value=mock_api_response,
        ) as mock_create_patch,
        pytest.raises(ValueError, match=IDENTICAL_PATCH_ERROR_MESSAGE),
    ):
        variable_definition.create_patch_from_file(
            file_path=VARIABLE_DEFINITION_EDITING_FILES_DIR
            / "variable_definition_var_test_wypvb3wd_2025-09-18T14-19-28.yaml",
        )

    mock_create_patch.assert_not_called()


def test_create_patch_from_file_path_not_set(variable_definition: VariableDefinition):
    my_patch = variable_definition
    my_patch.set_file_path(file_path=None)
    with pytest.raises(FileNotFoundError, match="Could not deduce a path to the file"):
        my_patch.create_patch_from_file()


def test_create_patch_from_file_path_non_existing(
    variable_definition: VariableDefinition,
):
    my_patch = variable_definition
    with pytest.raises(FileNotFoundError):
        my_patch.create_patch_from_file("some_file.yaml")


def test_create_validity_period_from_file(variable_definition: VariableDefinition):
    mock_api_response = MagicMock(name="VariableDefinition")
    mock_api_response.valid_from = "2025-01-01"
    mock_api_response.definition = {
        "nb": "Ny definition",
        "nn": "Ny definition",
        "en": "New definition",
    }

    with patch.object(
        VariableDefinition,
        "create_validity_period",
        return_value=mock_api_response,
    ) as mock_create_validity_period:
        prev_variable_definition = variable_definition
        result = prev_variable_definition.create_validity_period_from_file(
            file_path=VARIABLE_DEFINITION_EDITING_FILES_DIR
            / "date_and_definition.yaml",
        )
    assert result.definition != prev_variable_definition.definition
    assert result.valid_from != prev_variable_definition.valid_from
    mock_create_validity_period.assert_called_once()


def test_create_draft_with_special_characters():
    mock_api_response = MagicMock(name="VariableDefinition")
    mock_api_response.definition = {
        "nb": "Varigheten av en konflikt måles i antall tapte arbeidsdager, dvs. virkedager per uke for den aktuelle gruppen i konflikt, ikke kalenderdager. Det kan innebære mange spesialtegn som : og ;",
        "nn": "",
        "en": "Duration of an industrial disputes contains in number of work-days lost, i.e. working-days a week to the actual group in work stoppages, not calendar days.",
    }

    with patch.object(
        Vardef,
        "create_draft_from_file",
        return_value=mock_api_response,
    ) as mock_create_draft:
        result = Vardef.create_draft_from_file(
            file_path=VARIABLE_DEFINITION_EDITING_FILES_DIR
            / "variable_definition_landbak_wypvb3wd_2025-05-02T10-06-20.yaml",
        )
    assert ":" in result.definition["nb"]
    assert result.definition["nn"] == ""
    mock_create_draft.assert_called_once()


def test_update_draft_with_special_characters(variable_definition: VariableDefinition):
    mock_api_response = MagicMock(name="VariableDefinition")
    mock_api_response.definition = {
        "nb": "Ny definition med :",
        "nn": "Ny definition med %&",
        "en": "New definition",
    }

    with patch.object(
        VariableDefinition,
        "update_draft",
        return_value=mock_api_response,
    ) as mock_update_draft:
        prev_variable_definition = variable_definition
        result = prev_variable_definition.update_draft_from_file(
            file_path=VARIABLE_DEFINITION_EDITING_FILES_DIR
            / "variable_definition_landbak_wypvb3wd_2025-05-02T10-06-20.yaml",
        )
    assert result.definition != prev_variable_definition.definition
    assert ":" in result.definition["nb"]
    assert "&" in result.definition["nn"]
    mock_update_draft.assert_called_once()


def test_create_validity_period_from_file_path_not_set(
    variable_definition: VariableDefinition,
):
    variable_definition.set_file_path(file_path=None)
    with pytest.raises(FileNotFoundError, match="Could not deduce a path to the file"):
        variable_definition.create_patch_from_file()


def test_create_validity_period_from_file_path_non_existing(
    variable_definition: VariableDefinition,
):
    with pytest.raises(FileNotFoundError):
        variable_definition.create_validity_period_from_file("some_file.yaml")


@patch.object(VariableDefinition, "update_draft")
@patch.object(VariableDefinition, "create_patch")
@pytest.mark.parametrize(("initial_status"), list(VariableStatus))
@pytest.mark.parametrize(
    ("method_name", "expected_status"),
    [
        ("publish_internal", VariableStatus.PUBLISHED_INTERNAL),
        ("publish_external", VariableStatus.PUBLISHED_EXTERNAL),
    ],
)
def test_publish_methods(
    mock_create_patch: MagicMock,
    mock_update_draft: MagicMock,
    variable_definition: VariableDefinition,
    initial_status: VariableStatus,
    method_name: str,
    expected_status: VariableStatus,
):
    variable_definition.variable_status = initial_status
    method_to_call = getattr(variable_definition, method_name)
    if initial_status is VariableStatus.PUBLISHED_EXTERNAL:
        # It doesn't make sense to publish other statuses internally
        with pytest.raises(ValueError, match="That won't work here."):
            method_to_call()
    elif method_name == "publish_internal":
        if initial_status is VariableStatus.DRAFT:
            # Normal publishing flow
            method_to_call()
            mock_update_draft.assert_called_once_with(
                UpdateDraft(variable_status=expected_status),
            )
            mock_create_patch.assert_not_called()
        else:
            # It doesn't make sense to publish other statuses internally
            with pytest.raises(ValueError, match="That won't work here."):
                method_to_call()
    else:
        method_to_call()
        mock_update_draft.assert_not_called()
        mock_create_patch.assert_called_once_with(
            Patch(variable_status=VariableStatus.PUBLISHED_EXTERNAL),
        )


def test_str(variable_definition):
    assert (
        str(variable_definition)
        == """id: "wypvb3wd"
patch_id: 1
name:
    nb: |-
        test
    nn: |-
        test
    en: |-
        test
short_name: "var_test"
definition:
    nb: |-
        test
    nn: |-
        test
    en: |-
        test
classification_reference: "91"
unit_types:
    - "01"
subject_fields:
    - "a"
    - "b"
contains_special_categories_of_personal_data: true
variable_status: PUBLISHED_EXTERNAL
measurement_type: "test"
valid_from: '2024-11-01'
valid_until:
external_reference_uri: "http://www.example.com"
comment:
    nb: |-
        test
    nn: |-
        test
    en: |-
        test
related_variable_definition_uris:
    - "http://www.example.com"
owner:
    team: "my_team"
    groups:
        - "my_team_developers"
contact:
    title:
        nb: |-
            test
        nn: |-
            test
        en: |-
            test
    email: me@example.com
created_at: '2024-11-01T00:00:00'
created_by: "ano@ssb.no"
last_updated_at: '2024-11-01T00:00:00'
last_updated_by: "ano@ssb.no"
"""
    )


@pytest.mark.parametrize("method_name", ["publish_internal", "publish_external"])
@pytest.mark.parametrize(
    ("mocked_host", "should_raise"),
    [
        ("https://metadata.intern.ssb.no", True),
        ("https://metadata.intern.test.ssb.no", False),
    ],
)
@pytest.mark.parametrize(("initial_status"), list(VariableStatus))
@patch.object(VariableDefinition, "update_draft")
@patch.object(VariableDefinition, "create_patch")
@patch("dapla_metadata.variable_definitions._utils._client.VardefClient.get_config")
def test_block_publish_methods(
    mock_get_config: MagicMock,
    mock_update_draft: MagicMock,
    mock_create_patch: MagicMock,
    method_name: str,
    mocked_host: str,
    should_raise: bool,
    variable_definition: VariableDefinition,
    initial_status: VariableStatus,
):
    mock_config = MagicMock()
    mock_config.host = mocked_host
    mock_get_config.return_value = mock_config

    client = VardefClient()
    config = client.get_config()
    assert config is not None
    assert config.host == mocked_host

    variable_definition.variable_status = initial_status

    method = getattr(variable_definition, method_name)
    if should_raise:
        with pytest.raises(
            PublishingBlockedError, match=PUBLISHING_BLOCKED_ERROR_MESSAGE
        ):
            method()
        mock_update_draft.assert_not_called()
        mock_create_patch.assert_not_called()

    else:
        try:
            method()
            assert mock_update_draft.called or mock_create_patch.called
        except ValueError:
            # Ignore other exceptions for publishing
            contextlib.suppress(ValueError)


@pytest.mark.parametrize(
    ("mocked_host", "update_status", "should_raise"),
    [
        (
            VARDEF_PROD_URL,
            VariableStatus.PUBLISHED_INTERNAL.value,
            True,
        ),
        (
            VARDEF_PROD_URL,
            VariableStatus.PUBLISHED_EXTERNAL.value,
            True,
        ),
        (VARDEF_PROD_URL, VariableStatus.DRAFT.value, False),
        (VARDEF_TEST_URL, VariableStatus.DRAFT.value, False),
        (
            VARDEF_TEST_URL,
            VariableStatus.PUBLISHED_INTERNAL.value,
            False,
        ),
        (
            VARDEF_TEST_URL,
            VariableStatus.PUBLISHED_EXTERNAL.value,
            False,
        ),
    ],
)
@patch("dapla_metadata.variable_definitions._utils._client.VardefClient.get_config")
def test_block_update_variable_status(
    mock_get_config: MagicMock,
    mocked_host: str,
    update_status,
    should_raise: bool,
    variable_definition: VariableDefinition,
):
    mock_config = MagicMock()
    mock_config.host = mocked_host
    mock_get_config.return_value = mock_config

    client = VardefClient()
    config = client.get_config()
    assert config is not None
    assert config.host == mocked_host

    variable_definition.variable_status = VariableStatus.DRAFT

    with patch.object(
        VariableDefinition, "update_draft", wraps=variable_definition.update_draft
    ):
        update = UpdateDraft(variable_status=update_status)

        if should_raise:
            with pytest.raises(
                PublishingBlockedError, match=PUBLISHING_BLOCKED_ERROR_MESSAGE
            ):
                variable_definition.update_draft(update)
        else:
            try:
                variable_definition.update_draft(update)
            except ValueError:
                # Ignore other exceptions for publishing
                contextlib.suppress(ValueError)
