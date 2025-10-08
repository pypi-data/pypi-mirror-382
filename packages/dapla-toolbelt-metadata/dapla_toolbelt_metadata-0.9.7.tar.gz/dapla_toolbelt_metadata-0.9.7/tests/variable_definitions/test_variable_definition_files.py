"""Tests for variable definition files."""

import logging
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pytest
import pytz
from pytest_mock import MockerFixture
from ruamel.yaml import YAML

from dapla_metadata.variable_definitions._generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions._utils.config import WORKSPACE_DIR
from dapla_metadata.variable_definitions._utils.constants import TEMPLATE_HEADER
from dapla_metadata.variable_definitions._utils.constants import (
    TEMPLATE_SECTION_HEADER_MACHINE_GENERATED,
)
from dapla_metadata.variable_definitions._utils.constants import (
    TEMPLATE_SECTION_HEADER_OWNER,
)
from dapla_metadata.variable_definitions._utils.constants import (
    TEMPLATE_SECTION_HEADER_STATUS,
)
from dapla_metadata.variable_definitions._utils.files import _get_workspace_dir
from dapla_metadata.variable_definitions._utils.files import configure_yaml
from dapla_metadata.variable_definitions._utils.template_files import (
    _find_latest_template_file,
)
from dapla_metadata.variable_definitions._utils.template_files import (
    create_template_yaml,
)
from dapla_metadata.variable_definitions.exceptions import VardefFileError
from dapla_metadata.variable_definitions.vardef import Vardef
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID
from tests.utils.constants import VARDEF_EXAMPLE_SHORT_NAME
from tests.variable_definitions.conftest import VARIABLE_DEFINITION_DICT

yaml = YAML()
configure_yaml(yaml)


def test_yaml_file_creation(work_folder_defaults: Path):
    """Test if the function generates a YAML file."""
    file_path = work_folder_defaults
    assert file_path.exists(), "YAML file was not created"


def test_yaml_content_default_values(work_folder_defaults: Path):
    """Check if the generated YAML file with default values contains the expected data."""
    with work_folder_defaults.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "DRAFT"
    assert parsed_yaml["owner"]["team"] == "default team"
    assert parsed_yaml["name"]["nn"] is None


def test_yaml_content_saved_values(work_folder_variable_definition: Path) -> None:
    """Check if the generated YAML file with saved values contains the expected data."""
    with work_folder_variable_definition.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "PUBLISHED_EXTERNAL"
    assert parsed_yaml["last_updated_by"] == "ano@ssb.no"


def test_yaml_content_from_model_variable_definition(
    work_folder_variable_definition: Path,
) -> None:
    """Check if the generated YAML file with saved values contains the expected data."""
    with work_folder_variable_definition.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "PUBLISHED_EXTERNAL"
    assert parsed_yaml["last_updated_by"] == "ano@ssb.no"


def test_yaml_comments(work_folder_defaults: Path):
    """Ensure the YAML file includes the expected header comments."""
    with work_folder_defaults.open(encoding="utf-8") as f:
        content = f.read()

    assert TEMPLATE_HEADER in content
    assert TEMPLATE_SECTION_HEADER_STATUS.strip() in content.strip()
    assert TEMPLATE_SECTION_HEADER_OWNER.strip() in content.strip()
    assert TEMPLATE_SECTION_HEADER_MACHINE_GENERATED.strip() in content.strip()


def test_file_name(work_folder_defaults: Path):
    """Check filename."""
    assert "variable_definition_template_" in str(work_folder_defaults)


def test_workspace_fixture(set_temp_workspace: Path, tmp_path: Path):
    workspace = set_temp_workspace
    assert workspace.exists()
    assert workspace == tmp_path / "work"


@pytest.mark.usefixtures("set_temp_workspace")
def test_get_workspace_dir_without_env_var():
    workspace_dir = _get_workspace_dir()
    assert workspace_dir.exists()
    assert workspace_dir.is_dir()


def test_generate_yaml_from_dict() -> None:
    """Check if the generated YAML file with saved values contains the expected data."""
    with pytest.raises(AttributeError) as exc_info:
        create_template_yaml(
            VARIABLE_DEFINITION_DICT,  # type: ignore[arg-type]
            custom_directory=None,
        )
    assert str(exc_info.value) == "'dict' object has no attribute 'model_dump'"


def test_find_latest_template_file(mocker: MockerFixture, tmp_path: Path):
    mock_time = mocker.patch(
        "dapla_metadata.variable_definitions._utils.variable_definition_files._get_current_time",
    )

    def fast_forward(seconds: int) -> str:
        return str(
            datetime.now(pytz.timezone("Europe/Oslo")) + timedelta(seconds=seconds),
        )

    # Create three template files and one other
    # We need to fast-forward time to avoid all the files being named identically
    mock_time.return_value = fast_forward(0)
    create_template_yaml(custom_directory=tmp_path)
    mock_time.return_value = fast_forward(30)
    create_template_yaml(custom_directory=tmp_path)
    mock_time.return_value = fast_forward(60)
    third = create_template_yaml(custom_directory=tmp_path)
    (tmp_path / "random_file.yaml").touch()

    assert _find_latest_template_file(directory=tmp_path) == third


def test_find_latest_template_file_none_exist(tmp_path: Path):
    assert _find_latest_template_file(directory=tmp_path) is None


def test_logging_workspace_dir(caplog):
    """Test logging intended for debugging."""
    caplog.set_level(logging.DEBUG)
    _get_workspace_dir()
    assert "WORKSPACE_DIR' value:" in caplog.text


def test_workspace_dir_not_set(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(WORKSPACE_DIR, raising=False)
    with pytest.raises(
        VardefFileError,
        match="VardefFileError: WORKSPACE_DIR is not set",
    ):
        _get_workspace_dir()


def test_workspace_dir_doesnt_exist(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(WORKSPACE_DIR, "funnypath/haha")
    with pytest.raises(FileNotFoundError):
        _get_workspace_dir()


def test_workspace_is_not_dir(monkeypatch: pytest.MonkeyPatch, set_workspace_not_dir):
    monkeypatch.setenv(WORKSPACE_DIR, str(set_workspace_not_dir))
    with pytest.raises(NotADirectoryError):
        _get_workspace_dir()


def test_write_existing_variable_to_file():
    file_name = (
        Vardef.get_variable_definition_by_id(
            variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        )
        .to_file()
        .get_file_path()
    )
    with file_name.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == VariableStatus.DRAFT
    assert parsed_yaml["short_name"] == VARDEF_EXAMPLE_SHORT_NAME


def test_write_existing_variable_to_file_by_short_name():
    file_name = (
        Vardef.get_variable_definition_by_shortname(
            short_name=VARDEF_EXAMPLE_SHORT_NAME,
        )
        .to_file()
        .get_file_path()
    )
    with file_name.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == VariableStatus.DRAFT
    assert parsed_yaml["short_name"] == VARDEF_EXAMPLE_SHORT_NAME


def test_shortname_and_id_in_filename():
    file_name = (
        Vardef.get_variable_definition_by_id(
            variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        )
        .to_file()
        .get_file_path()
    )

    assert (
        f"variable_definition_{VARDEF_EXAMPLE_SHORT_NAME}_{VARDEF_EXAMPLE_DEFINITION_ID}_"
        in str(file_name)
    )
