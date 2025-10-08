import pytest

from dapla_metadata._shared.config import DAPLA_GROUP_CONTEXT
from dapla_metadata._shared.config import DAPLA_REGION
from dapla_metadata._shared.config import DAPLA_SERVICE
from dapla_metadata._shared.config import JUPYTERHUB_USER
from dapla_metadata._shared.config import OIDC_TOKEN
from dapla_metadata._shared.enums import DaplaRegion
from dapla_metadata._shared.enums import DaplaService
from dapla_metadata.dapla import user_info
from dapla_metadata.dapla.user_info import DaplaLabUserInfo
from dapla_metadata.dapla.user_info import JupyterHubUserInfo
from dapla_metadata.dapla.user_info import TestUserInfo
from dapla_metadata.dapla.user_info import UnknownUserInfo
from dapla_metadata.dapla.user_info import UserInfo


@pytest.mark.parametrize(
    ("environment_variable_name", "environment_variable_value", "expected_class"),
    [
        (DAPLA_SERVICE, DaplaService.JUPYTERLAB.value, JupyterHubUserInfo),
        (DAPLA_REGION, DaplaRegion.DAPLA_LAB.value, DaplaLabUserInfo),
        (None, None, UnknownUserInfo),
    ],
)
def test_get_user_info_for_current_platform(
    monkeypatch: pytest.MonkeyPatch,
    environment_variable_name: str,
    environment_variable_value: str,
    expected_class: type[UserInfo],
):
    if environment_variable_name:
        monkeypatch.setenv(environment_variable_name, environment_variable_value)
    assert isinstance(user_info.get_user_info_for_current_platform(), expected_class)


def test_jupyterhub_user_info_short_email(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(JUPYTERHUB_USER, TestUserInfo.PLACEHOLDER_EMAIL_ADDRESS)
    assert JupyterHubUserInfo().short_email == TestUserInfo.PLACEHOLDER_EMAIL_ADDRESS


def test_dapla_lab_user_info_short_email(
    fake_jwt: str,
    raw_jwt_payload: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv(OIDC_TOKEN, fake_jwt)
    assert DaplaLabUserInfo().short_email == raw_jwt_payload["email"]


def test_dapla_lab_user_info_short_email_no_jwt_available(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv(OIDC_TOKEN, raising=False)
    assert DaplaLabUserInfo().short_email is None


@pytest.mark.parametrize(("raw_jwt_payload"), [{"no_email": "no_email_in_jwt"}])
def test_dapla_lab_user_info_short_email_no_email_in_jwt(
    fake_jwt: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv(OIDC_TOKEN, fake_jwt)
    assert DaplaLabUserInfo().short_email is None


@pytest.mark.parametrize(
    ("environment_variable_name", "environment_variable_value", "expected_team"),
    [
        (DAPLA_GROUP_CONTEXT, "dapla-metadata-developers", "dapla-metadata"),
        (
            DAPLA_GROUP_CONTEXT,
            "dapla-metadata-data-admins",
            "dapla-metadata",
        ),
        (DAPLA_GROUP_CONTEXT, "dapla-metadata-dev", "dapla-metadata"),
        (DAPLA_GROUP_CONTEXT, "dapla-metadata", "dapla"),
        (
            DAPLA_GROUP_CONTEXT,
            "dapla-metadata-not-a-real-group",
            "dapla-metadata-not-a-real",
        ),
    ],
)
def test_get_current_team_dapla_lab(
    monkeypatch: pytest.MonkeyPatch,
    environment_variable_name: str,
    environment_variable_value: str,
    expected_team: str,
):
    monkeypatch.setenv(DAPLA_REGION, DaplaRegion.DAPLA_LAB)
    if environment_variable_name:
        monkeypatch.setenv(environment_variable_name, environment_variable_value)
    assert user_info.get_user_info_for_current_platform().current_team == expected_team


@pytest.mark.parametrize(
    ("environment_variable_value"),
    [
        None,
        "",
    ],
)
def test_get_owner_errors_dapla_lab(
    monkeypatch: pytest.MonkeyPatch,
    environment_variable_value: str | None,
):
    monkeypatch.setenv(DAPLA_REGION, DaplaRegion.DAPLA_LAB)
    if environment_variable_value is None:
        monkeypatch.delenv(DAPLA_GROUP_CONTEXT, raising=False)
    else:
        monkeypatch.setenv(DAPLA_GROUP_CONTEXT, environment_variable_value)

    with pytest.raises(
        OSError,
        match="DAPLA_GROUP_CONTEXT environment variable not found",
    ):
        user_info.get_user_info_for_current_platform().current_team  # noqa: B018
