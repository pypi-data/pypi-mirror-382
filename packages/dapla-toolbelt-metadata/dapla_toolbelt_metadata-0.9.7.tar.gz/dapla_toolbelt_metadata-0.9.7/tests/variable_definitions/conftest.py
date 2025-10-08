import os
import traceback
from collections.abc import Generator
from datetime import date
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import docker
import pytest

from dapla_metadata._shared.config import DAPLA_GROUP_CONTEXT
from dapla_metadata.variable_definitions._generated import vardef_client
from dapla_metadata.variable_definitions._generated.vardef_client.api_client import (
    ApiClient,
)
from dapla_metadata.variable_definitions._generated.vardef_client.configuration import (
    Configuration,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.contact import (
    Contact,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.draft import (
    Draft,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.language_string_type import (
    LanguageStringType,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.owner import (
    Owner,
)
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
from dapla_metadata.variable_definitions._utils.config import WORKSPACE_DIR
from dapla_metadata.variable_definitions._utils.constants import (
    VARIABLE_DEFINITIONS_DIR,
)
from dapla_metadata.variable_definitions._utils.template_files import (
    create_template_yaml,
)
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition
from tests.utils.constants import VARDEF_EXAMPLE_ACTIVE_GROUP
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID
from tests.utils.constants import VARDEF_EXAMPLE_INVALID_ID
from tests.utils.microcks_testcontainer import MicrocksContainer
from tests.variable_definitions.constants import OPENAPI_DIR


class CouldNotInstantiateTestContainerError(RuntimeError):
    def __init__(self):
        """To be raised when the TestContainer cannot be instantiated."""
        super().__init__(
            "Could not instantiate the TestContainer. Please check that your local Docker is correctly configured."
        )


@pytest.fixture(autouse=True)
def _set_dapla_group_context(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv(DAPLA_GROUP_CONTEXT, VARDEF_EXAMPLE_ACTIVE_GROUP)


@pytest.fixture(scope="session")
def vardef_mock_service() -> Generator[MicrocksContainer | None]:
    try:
        with MicrocksContainer() as container:
            container.upload_primary_artifact(
                str(OPENAPI_DIR / "variable-definitions-internal.yml"),
            )
            yield container
    except docker.errors.DockerException as e:
        traceback.print_exception(e)
        yield None


@pytest.fixture(scope="session")
def client_configuration(
    vardef_mock_service: MicrocksContainer | None,
) -> Configuration:
    if vardef_mock_service is None:
        raise CouldNotInstantiateTestContainerError
    return vardef_client.Configuration(
        host=vardef_mock_service.get_mock_url(),
        access_token="test_dummy",  # noqa: S106
    )


@pytest.fixture(autouse=True, scope="session")
def _configure_vardef_client(client_configuration):
    VardefClient.set_config(client_configuration)


@pytest.fixture(autouse=True)
def set_temp_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Fixture which set env WORKSPACE_DIR to tmp path/work."""
    workspace_dir = tmp_path / "work"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv(WORKSPACE_DIR, str(workspace_dir))
    return workspace_dir


@pytest.fixture
def api_client(client_configuration) -> Generator[ApiClient]:
    with vardef_client.ApiClient(client_configuration) as api_client:
        yield api_client


@pytest.fixture
def language_string_type() -> LanguageStringType:
    return LanguageStringType(nb="test", nn="test", en="test")


@pytest.fixture
def contact(language_string_type) -> Contact:
    return Contact(title=language_string_type, email="me@example.com")


@pytest.fixture
def owner() -> Owner:
    return Owner(team="my_team", groups=["my_team_developers"])


@pytest.fixture
def draft(language_string_type, contact) -> Draft:
    return Draft(
        name=language_string_type,
        short_name="test",
        definition=language_string_type,
        classification_reference="91",
        unit_types=["01"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
    )


def sample_variable_definition() -> VariableDefinition:
    return VariableDefinition(
        id=VARDEF_EXAMPLE_DEFINITION_ID,
        patch_id=1,
        name=LanguageStringType(nb="test", nn="test", en="test"),
        short_name="var_test",
        definition=LanguageStringType(nb="test", nn="test", en="test"),
        classification_reference="91",
        unit_types=["01"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        valid_until=None,
        external_reference_uri="http://www.example.com",
        comment=LanguageStringType(nb="test", nn="test", en="test"),
        related_variable_definition_uris=["http://www.example.com"],
        contact=Contact(
            title=LanguageStringType(nb="test", nn="test", en="test"),
            email="me@example.com",
        ),
        owner=Owner(team="my_team", groups=["my_team_developers"]),
        created_at=date(2024, 11, 1),
        created_by="ano@ssb.no",
        last_updated_at=date(2024, 11, 1),
        last_updated_by="ano@ssb.no",
    )


def unknown_variable_definition() -> VariableDefinition:
    unknown = sample_variable_definition()
    unknown.id = VARDEF_EXAMPLE_INVALID_ID
    return unknown


@pytest.fixture
def variable_definition() -> VariableDefinition:
    return sample_variable_definition()


@pytest.fixture
def update_draft(language_string_type, contact, owner) -> UpdateDraft:
    return UpdateDraft(
        name=language_string_type,
        short_name="test",
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
        owner=owner,
    )


@pytest.fixture
def validity_period(language_string_type, contact) -> ValidityPeriod:
    return ValidityPeriod(
        name=language_string_type,
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
    )


@pytest.fixture
def patch_fixture(language_string_type, contact, owner) -> Patch:
    return Patch(
        name=language_string_type,
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
        owner=owner,
    )


def sample_complete_patch_output() -> VariableDefinition:
    return VariableDefinition(
        id=VARDEF_EXAMPLE_DEFINITION_ID,
        patch_id=1,
        name=LanguageStringType(nb="test", nn="test", en="test"),
        short_name="var_test",
        definition=LanguageStringType(nb="test", nn="test", en="test"),
        classification_reference="91",
        unit_types=["01"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_INTERNAL,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        valid_until=None,
        external_reference_uri="http://www.example.com",
        comment=LanguageStringType(nb="test", nn="test", en="test"),
        related_variable_definition_uris=["http://www.example.com"],
        contact=Contact(
            title=LanguageStringType(nb="test", nn="test", en="test"),
            email="me@example.com",
        ),
        owner=Owner(team="my_team", groups=["my_team_developers"]),
        created_at=date(2024, 11, 1),
        created_by="ano@ssb.no",
        last_updated_at=date(2024, 11, 1),
        last_updated_by="ano@ssb.no",
    )


@pytest.fixture
def mock_update_variable_definition_by_id():
    return Mock(
        return_value=CompleteResponse(
            id="test-id",
            patch_id=1,
            name=LanguageStringType(en="Name", nb="Navn"),
            short_name="short-name",
            definition=LanguageStringType(en="Definition", nb="Definition"),
            unit_types=["unit-type"],
            subject_fields=["subject-field"],
            contains_special_categories_of_personal_data=False,
            variable_status=VariableStatus.DRAFT,
            valid_from=date(2023, 1, 1),
            owner=Owner(team="Owner", groups=["dapla-felles"]),
            contact=Contact(
                title=LanguageStringType(en="Contact", nb="Contact"),
                email="contact@contact.com",
            ),
            classification_reference="www.newurl.com",
            created_at=datetime(2023, 1, 1, 12, 0),  # noqa: DTZ001
            created_by="created by",
            last_updated_at=datetime(2023, 1, 1, 12, 0),  # noqa: DTZ001
            last_updated_by="updated by",
        ),
    )


@pytest.fixture
def complete_patch_output() -> VariableDefinition:
    return sample_complete_patch_output()


@pytest.fixture
def work_folder_defaults(set_temp_workspace: Path):
    """Fixture that ensures a work folder exists for template with default values."""
    base_path = set_temp_workspace
    file_name = create_template_yaml(
        custom_directory=base_path,
    )

    return base_path / file_name


@pytest.fixture
def work_folder_complete_patch_output(set_temp_workspace: Path):
    """Fixture that ensures a work folder exists for template with saved variable definition values."""
    base_path = set_temp_workspace / VARIABLE_DEFINITIONS_DIR
    file_name = create_template_yaml(
        sample_complete_patch_output(),
        custom_directory=base_path,
    )
    return base_path / file_name


@pytest.fixture
def _delete_workspace_dir_env_var(set_temp_workspace):  # noqa: ARG001
    original_workspace_dir = os.environ.get(WORKSPACE_DIR)

    if WORKSPACE_DIR in os.environ:
        del os.environ[WORKSPACE_DIR]

    yield

    if original_workspace_dir is not None:
        os.environ[WORKSPACE_DIR] = original_workspace_dir
    else:
        pass


@pytest.fixture
def work_folder_variable_definition(set_temp_workspace: Path):
    """Fixture that ensures a work folder exists for template with saved variable definition values."""
    base_path = set_temp_workspace
    file_name = create_template_yaml(
        sample_variable_definition(),
        custom_directory=base_path,
    )
    return base_path / file_name


VARIABLE_DEFINITION_DICT = {
    "name": {
        "en": "Country Background",
        "nb": "Landbakgrunn",
        "nn": "Landbakgrunn",
    },
    "short_name": "new_short_name1",
    "definition": {
        "en": "Country background is the person's own, the mother's or possibly the father's country of birth. Persons without an immigrant background always have Norway as country background. In cases where the parents have different countries of birth the mother's country of birth is chosen. If neither the person nor the parents are born abroad, country background is chosen from the first person born abroad in the order mother's mother, mother's father, father's mother, father's father.",
        "nb": "For personer født i utlandet, er dette (med noen få unntak) eget fødeland. For personer født i Norge er det foreldrenes fødeland. I de tilfeller der foreldrene har ulikt fødeland, er det morens fødeland som blir valgt. Hvis ikke personen selv eller noen av foreldrene er utenlandsfødt, hentes landbakgrunn fra de første utenlandsfødte en treffer på i rekkefølgen mormor, morfar, farmor eller farfar.",
        "nn": "For personar fødd i utlandet, er dette (med nokre få unntak) eige fødeland. For personar fødd i Noreg er det fødelandet til foreldra. I dei tilfella der foreldra har ulikt fødeland, er det fødelandet til mora som blir valt. Viss ikkje personen sjølv eller nokon av foreldra er utenlandsfødt, blir henta landsbakgrunn frå dei første utenlandsfødte ein treffar på i rekkjefølgja mormor, morfar, farmor eller farfar.",
    },
    "classification_reference": "91",
    "unit_types": ["01", "02"],
    "subject_fields": ["he04"],
    "contains_special_categories_of_personal_data": True,
    "measurement_type": None,
    "valid_from": "2003-01-01",
    "external_reference_uri": "https://www.ssb.no/a/metadata/conceptvariable/vardok/1919/nb",
    "comment": {
        "nb": "Fra og med 1.1.2003 ble definisjon endret til også å trekke inn besteforeldrenes fødeland.",
        "nn": "Fra og med 1.1.2003 ble definisjon endret til også å trekke inn besteforeldrenes fødeland.",
        "en": "As of 1 January 2003, the definition was changed to also include the grandparents' country of birth.",
    },
    "related_variable_definition_uris": ["https://example.com/"],
    "contact": {
        "title": {
            "en": "Division for population statistics",
            "nb": "Seksjon for befolkningsstatistikk",
            "nn": "Seksjon for befolkningsstatistikk",
        },
        "email": "s320@ssb.no",
    },
}


@pytest.fixture
def set_workspace_not_dir(tmp_path: Path):
    file_path = tmp_path / "funnyfiles.txt"
    file_path.write_text("This is a text file.")
    return file_path
