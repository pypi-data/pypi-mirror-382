from datetime import datetime
from datetime import timezone
from typing import Any

from dapla_metadata.datasets.compatibility._utils import DATADOC_KEY
from dapla_metadata.datasets.compatibility._utils import DATASET_KEY
from dapla_metadata.datasets.compatibility._utils import DOCUMENT_VERSION_KEY
from dapla_metadata.datasets.compatibility._utils import PSEUDONYMIZATION_KEY
from dapla_metadata.datasets.compatibility._utils import VARIABLES_KEY
from dapla_metadata.datasets.compatibility._utils import add_container
from dapla_metadata.datasets.compatibility._utils import cast_to_date_type
from dapla_metadata.datasets.compatibility._utils import convert_datetime_to_date
from dapla_metadata.datasets.compatibility._utils import convert_is_personal_data
from dapla_metadata.datasets.compatibility._utils import copy_pseudonymization_metadata
from dapla_metadata.datasets.compatibility._utils import (
    find_and_update_language_strings,
)
from dapla_metadata.datasets.compatibility._utils import remove_element_from_model


def handle_current_version(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle the current version of the metadata.

    This function returns the supplied metadata unmodified.

    Args:
        supplied_metadata: The metadata for the current version.

    Returns:
        The unmodified supplied metadata.
    """
    return supplied_metadata


def handle_version_6_0_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 6.1.0.

    This function modifies the supplied metadata to accommodate breaking changes
    introduced in version 6.1.0. Specifically, it:
    - Consolidates `use_restriction` and `use_restriction_date` into a list of
      dictionaries under `use_restrictions`.
    - Removes the old `use_restriction` and `use_restriction_date` fields.
    - It also converts `use_restriction_date` from datetime to date.

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        The upgraded metadata dictionary.
    """
    dataset = supplied_metadata[DATADOC_KEY][DATASET_KEY]

    use_restriction = dataset.get("use_restriction")
    if use_restriction is not None:
        converted_date = convert_datetime_to_date(dataset.get("use_restriction_date"))
        dataset["use_restrictions"] = [
            {
                "use_restriction_type": use_restriction,
                "use_restriction_date": converted_date,
            }
        ]
    else:
        dataset["use_restrictions"] = []

    for field in ("use_restriction", "use_restriction_date"):
        remove_element_from_model(dataset, field)

    return supplied_metadata


def handle_version_5_0_1(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 6.0.0.

    This function modifies the supplied metadata to accommodate breaking changes
    introduced in version 6.0.0. Specifically, it:
    - Moves the following fields from dataset to variable level:
        - contains_personal_data (becomes is_personal_data)
        - unit_type
        - data_source
        - temporality_type

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        The updated metadata dictionary.
    """
    fields = [
        ("contains_personal_data", "is_personal_data"),
        ("unit_type", "unit_type"),
        ("data_source", "data_source"),
        ("temporality_type", "temporality_type"),
    ]

    dataset: dict[str, Any] = supplied_metadata[DATADOC_KEY][DATASET_KEY]
    variables: list[dict[str, Any]] = supplied_metadata[DATADOC_KEY][VARIABLES_KEY]

    for f in fields:
        dataset_level_field_value = dataset.pop(f[0], None)
        for v in variables:
            if v.get(f[1]) is None:
                # Don't override any set values
                v[f[1]] = dataset_level_field_value

    return supplied_metadata


def handle_version_4_0_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 5.0.1.

    This function modifies the supplied metadata to accommodate breaking changes
    introduced in version 5.0.1. Specifically, it:
    - Copies pseudonymization metadata if pseudonymization is enabled.
    - Converts the 'is_personal_data' fields to be a bool.
    - All 'pseudonymization' from the container is removed.
    - It also updates the container version to 1.0.0 from 0.0.1

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        The updated metadata dictionary.
    """
    if supplied_metadata.get(PSEUDONYMIZATION_KEY):
        copy_pseudonymization_metadata(supplied_metadata)

    convert_is_personal_data(supplied_metadata)

    remove_element_from_model(supplied_metadata, PSEUDONYMIZATION_KEY)
    supplied_metadata[DOCUMENT_VERSION_KEY] = "1.0.0"
    return supplied_metadata


def handle_version_3_3_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 3.3.0.

    This function modifies the supplied metadata to accommodate breaking changes
    introduced in version 4.0.0. Specifically, it removes the
    'direct_person_identifying' field from each variable in 'datadoc.variables'.

    Version 4.0.0 used an enum for is_personal_data, however this was changed to a bool again for version 5.0.1.
    We skip setting the enum here and just keep the value it has.

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        The updated metadata dictionary.
    """
    for variable in supplied_metadata[DATADOC_KEY][VARIABLES_KEY]:
        variable["is_personal_data"] = variable["direct_person_identifying"]
        remove_element_from_model(variable, "direct_person_identifying")

    return supplied_metadata


def handle_version_3_2_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 3.2.0.

    This function modifies the supplied metadata to accommodate breaking
    changes introduced in version 3.3.0. Specifically, it updates the
    'contains_data_from' and 'contains_data_until' fields in both the 'dataset'
    and 'variables' sections of the supplied metadata dictionary to ensure they
    are stored as date strings.

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        The updated metadata dictionary.
    """
    fields = ["contains_data_from", "contains_data_until"]
    for field in fields:
        supplied_metadata[DATADOC_KEY][DATASET_KEY][field] = cast_to_date_type(
            supplied_metadata[DATADOC_KEY][DATASET_KEY].get(field, None),
        )
        for v in supplied_metadata[DATADOC_KEY][VARIABLES_KEY]:
            v[field] = cast_to_date_type(v.get(field, None))

    return supplied_metadata


def handle_version_3_1_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 3.1.0.

    This function modifies the supplied metadata to accommodate breaking
    changes introduced in version 3.2.0. Specifically, it updates the
    'data_source' field in both the 'dataset' and 'variables' sections of the
    supplied metadata dictionary by converting value to string.

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        The updated metadata dictionary.
    """
    data = supplied_metadata[DATADOC_KEY][DATASET_KEY]["data_source"]

    if data is not None:
        supplied_metadata[DATADOC_KEY][DATASET_KEY]["data_source"] = str(
            data[0]["languageText"],
        )

    for i in range(len(supplied_metadata[DATADOC_KEY][VARIABLES_KEY])):
        data = supplied_metadata[DATADOC_KEY][VARIABLES_KEY][i]["data_source"]
        if data is not None:
            supplied_metadata[DATADOC_KEY][VARIABLES_KEY][i]["data_source"] = str(
                data[0]["languageText"],
            )

    return supplied_metadata


def handle_version_2_2_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 2.2.0.

    This function modifies the supplied metadata to accommodate breaking changes
    introduced in version 3.1.0. Specifically, it updates the 'subject_field' in
    the 'dataset' section of the supplied metadata dictionary by converting it to
    a string. It also removes the 'register_uri' field from the 'dataset'.
    Additionally, it removes 'sentinel_value_uri' from each variable,
    sets 'special_value' and 'custom_type' fields to None, and updates
    language strings in the 'variables' and 'dataset' sections.

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        The updated metadata dictionary.
    """
    if supplied_metadata[DATADOC_KEY][DATASET_KEY]["subject_field"] is not None:
        data = supplied_metadata[DATADOC_KEY][DATASET_KEY]["subject_field"]
        supplied_metadata[DATADOC_KEY][DATASET_KEY]["subject_field"] = str(
            data["nb"] or data["nn"] or data["en"],
        )

    remove_element_from_model(
        supplied_metadata[DATADOC_KEY][DATASET_KEY], "register_uri"
    )

    for i in range(len(supplied_metadata[DATADOC_KEY][VARIABLES_KEY])):
        remove_element_from_model(
            supplied_metadata[DATADOC_KEY][VARIABLES_KEY][i],
            "sentinel_value_uri",
        )
        supplied_metadata[DATADOC_KEY][VARIABLES_KEY][i]["special_value"] = None
        supplied_metadata[DATADOC_KEY][VARIABLES_KEY][i]["custom_type"] = None
        supplied_metadata[DATADOC_KEY][VARIABLES_KEY][i] = (
            find_and_update_language_strings(
                supplied_metadata[DATADOC_KEY][VARIABLES_KEY][i],
            )
        )
    supplied_metadata[DATADOC_KEY][DATASET_KEY]["custom_type"] = None
    supplied_metadata[DATADOC_KEY][DATASET_KEY] = find_and_update_language_strings(
        supplied_metadata[DATADOC_KEY][DATASET_KEY],
    )
    return supplied_metadata


def handle_version_2_1_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 2.1.0.

    This function modifies the supplied metadata to accommodate breaking changes
    introduced in version 2.2.0. Specifically, it updates the 'owner' field in
    the 'dataset' section of the supplied metadata dictionary by converting it
    from a LanguageStringType to a string.

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        The updated metadata dictionary.
    """
    data = supplied_metadata[DATASET_KEY]["owner"]
    supplied_metadata[DATASET_KEY]["owner"] = str(
        data["nb"] or data["nn"] or data["en"]
    )
    return add_container(supplied_metadata)


def handle_version_1_0_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 1.0.0.

    This function modifies the supplied metadata to accommodate breaking changes
    introduced in version 2.1.0. Specifically, it updates the date fields
    'metadata_created_date' and 'metadata_last_updated_date' to ISO 8601 format
    with UTC timezone. It also converts the 'data_source' field from a string to a
    dictionary with language keys if necessary and removes the 'data_source_path'
    field.

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        The updated metadata dictionary.

    """
    datetime_fields = [("metadata_created_date"), ("metadata_last_updated_date")]
    for field in datetime_fields:
        if supplied_metadata[DATASET_KEY][field]:
            supplied_metadata[DATASET_KEY][field] = datetime.isoformat(
                datetime.fromisoformat(
                    supplied_metadata[DATASET_KEY][field]
                ).astimezone(
                    tz=timezone.utc,
                ),
                timespec="seconds",
            )
    if isinstance(supplied_metadata[DATASET_KEY]["data_source"], str):
        supplied_metadata[DATASET_KEY]["data_source"] = {
            "en": supplied_metadata[DATASET_KEY]["data_source"],
            "nn": "",
            "nb": "",
        }

    remove_element_from_model(supplied_metadata[DATASET_KEY], "data_source_path")

    return supplied_metadata


def handle_version_0_1_1(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 0.1.1.

    This function modifies the supplied metadata to accommodate breaking changes
    introduced in version 1.0.0. Specifically, it renames certain keys within the
    `dataset` and `variables` sections, and replaces empty string values with
    `None` for `dataset` keys.

    Args:
        supplied_metadata: The metadata dictionary that needs to be updated.

    Returns:
        The updated metadata dictionary.

    References:
        PR ref: https://github.com/statisticsnorway/ssb-datadoc-model/pull/4
    """
    key_renaming = [
        ("metadata_created_date", "created_date"),
        ("metadata_created_by", "created_by"),
        ("metadata_last_updated_date", "last_updated_date"),
        ("metadata_last_updated_by", "last_updated_by"),
    ]
    for new_key, old_key in key_renaming:
        supplied_metadata[DATASET_KEY][new_key] = supplied_metadata[DATASET_KEY].pop(
            old_key,
        )
    # Replace empty strings with None, empty strings are not valid for LanguageStrings values
    supplied_metadata[DATASET_KEY] = {
        k: None if v == "" else v for k, v in supplied_metadata[DATASET_KEY].items()
    }

    key_renaming = [("data_type", "datatype")]

    for i in range(len(supplied_metadata[VARIABLES_KEY])):
        for new_key, old_key in key_renaming:
            supplied_metadata[VARIABLES_KEY][i][new_key] = supplied_metadata[
                VARIABLES_KEY
            ][i].pop(
                old_key,
            )

    return supplied_metadata
