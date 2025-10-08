"""Simple tests for basic coverage of the generated client."""

from dapla_metadata.variable_definitions._generated import vardef_client
from dapla_metadata.variable_definitions._generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from tests.utils.constants import VARDEF_EXAMPLE_ACTIVE_GROUP
from tests.utils.constants import VARDEF_EXAMPLE_DATE
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID


def test_create_draft(api_client, draft):
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    definition = api_instance.create_variable_definition(
        VARDEF_EXAMPLE_ACTIVE_GROUP,
        draft,
    )
    assert isinstance(definition, CompleteResponse)


def test_update_draft(api_client, update_draft):
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    definition = api_instance.update_variable_definition_by_id(
        VARDEF_EXAMPLE_DEFINITION_ID,
        VARDEF_EXAMPLE_ACTIVE_GROUP,
        update_draft,
    )
    assert isinstance(definition, CompleteResponse)


def test_delete_draft(api_client):
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    response = api_instance.delete_variable_definition_by_id(
        VARDEF_EXAMPLE_DEFINITION_ID,
        VARDEF_EXAMPLE_ACTIVE_GROUP,
    )
    assert response is None


def test_list_variable_definitions(api_client):
    api_instance = vardef_client.VariableDefinitionsApi(api_client)
    definitions = api_instance.list_variable_definitions(
        date_of_validity=VARDEF_EXAMPLE_DATE,
    )
    assert isinstance(definitions[0], CompleteResponse)


def test_get_variable_definition(api_client):
    api_instance = vardef_client.VariableDefinitionsApi(api_client)
    definition = api_instance.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        date_of_validity=VARDEF_EXAMPLE_DATE,
    )
    assert isinstance(definition, CompleteResponse)


def test_list_validity_periods(api_client):
    api_instance = vardef_client.ValidityPeriodsApi(api_client)
    validity_periods = api_instance.list_validity_periods(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(validity_periods[0], CompleteResponse)


def test_create_validity_period(api_client, validity_period):
    api_instance = vardef_client.ValidityPeriodsApi(api_client)
    validity_period = api_instance.create_validity_period(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        active_group=VARDEF_EXAMPLE_ACTIVE_GROUP,
        validity_period=validity_period,
    )
    assert isinstance(validity_period, CompleteResponse)


def test_list_patches(api_client):
    api_instance = vardef_client.PatchesApi(api_client)
    patches = api_instance.list_patches(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(patches[0], CompleteResponse)


def test_get_patch(api_client):
    api_instance = vardef_client.PatchesApi(api_client)
    patch = api_instance.get_patch(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        patch_id=1,
    )
    assert isinstance(patch, CompleteResponse)


def test_create_patch(api_client, patch_fixture):
    api_instance = vardef_client.PatchesApi(api_client)
    patch = api_instance.create_patch(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        active_group=VARDEF_EXAMPLE_ACTIVE_GROUP,
        valid_from=VARDEF_EXAMPLE_DATE,
        patch=patch_fixture,
    )
    assert isinstance(patch, CompleteResponse)
