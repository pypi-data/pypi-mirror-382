"""Tests for Vardef client exception handling."""

from http import HTTPStatus

from dapla_metadata.variable_definitions.exceptions import STATUS_EXPLANATIONS
from dapla_metadata.variable_definitions.exceptions import VardefClientError
from tests.utils.constants import CONSTRAINT_VIOLATION_BODY
from tests.utils.constants import CONSTRAINT_VIOLATION_BODY_MISSING_FIELD
from tests.utils.constants import CONSTRAINT_VIOLATION_BODY_MISSING_MESSAGES
from tests.utils.constants import CONSTRAINT_VIOLATION_BODY_MISSING_VIOLATIONS


def test_valid_response_body():
    response_body = '{"status": 400, "detail": "Bad Request"}'
    exc = VardefClientError(response_body)
    assert exc.status == HTTPStatus.BAD_REQUEST
    assert exc.detail == "\nDetail: Bad Request"
    assert str(exc) == STATUS_EXPLANATIONS[HTTPStatus.BAD_REQUEST] + exc.detail


def test_response_empty_status():
    response_body = '{"status": , "detail": "Bad Request"}'
    exc = VardefClientError(response_body)
    assert exc.status is None
    assert str(exc) == "Could not decode error response from API"


def test_no_status():
    response_body = '{"detail": "Bad Request"}'
    exc = VardefClientError(response_body)
    assert exc.status is None
    assert exc.detail == "\nDetail: Bad Request"


def test_no_explanation_for_status():
    assert (
        str(
            VardefClientError(
                f'{{"status": {HTTPStatus.IM_A_TEAPOT}, "detail": "{HTTPStatus.IM_A_TEAPOT.phrase}"}}',
            ),
        )
        == f"Status {HTTPStatus.IM_A_TEAPOT}:\nDetail: {HTTPStatus.IM_A_TEAPOT.phrase}"
    )


def test_invalid_json():
    response_body = "Not a JSON string"
    exc = VardefClientError(response_body)
    assert exc.status is None
    assert exc.detail == "Could not decode error response from API"
    assert str(exc) == "Could not decode error response from API"


def test_missing_keys():
    response_body = '{"status": 404}'
    exc = VardefClientError(response_body)
    assert exc.status == HTTPStatus.NOT_FOUND
    assert exc.detail is None
    assert str(exc) == STATUS_EXPLANATIONS[HTTPStatus.NOT_FOUND]


def test_constraint_violation():
    response_body = CONSTRAINT_VIOLATION_BODY
    exc = VardefClientError(response_body)
    assert exc.status == HTTPStatus.BAD_REQUEST
    assert exc.detail == (
        "\nDetail: "
        "\nupdateVariableDefinitionById.updateDraft.owner.team: Invalid Dapla team"
        "\nupdateVariableDefinitionById.updateDraft.owner.team: must not be empty"
    )


def test_constraint_violation_missing_messages():
    response_body = CONSTRAINT_VIOLATION_BODY_MISSING_MESSAGES
    exc = VardefClientError(response_body)
    assert exc.status == HTTPStatus.BAD_REQUEST
    assert exc.detail == (
        "\nDetail: "
        "\nupdateVariableDefinitionById.updateDraft.owner.team: No message provided"
        "\nupdateVariableDefinitionById.updateDraft.owner.team: No message provided"
    )


def test_constraint_violation_empty_violations():
    response_body = CONSTRAINT_VIOLATION_BODY_MISSING_VIOLATIONS
    exc = VardefClientError(response_body)
    assert exc.status == HTTPStatus.BAD_REQUEST
    assert str(exc) == f"{STATUS_EXPLANATIONS[HTTPStatus.BAD_REQUEST]}\nDetail: \n"


def test_constraint_violation_empty_field():
    response_body = CONSTRAINT_VIOLATION_BODY_MISSING_FIELD
    exc = VardefClientError(response_body)
    assert exc.status == HTTPStatus.BAD_REQUEST
    assert exc.detail == (
        "\nDetail: "
        "\nUnknown field: Invalid Dapla team"
        "\nUnknown field: must not be empty"
    )
