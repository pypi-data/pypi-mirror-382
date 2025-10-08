from datetime import datetime
from typing import Any

import arrow

DOCUMENT_VERSION_KEY = "document_version"
DATADOC_KEY = "datadoc"
DATASET_KEY = "dataset"
VARIABLES_KEY = "variables"
PSEUDONYMIZATION_KEY = "pseudonymization"


class UnknownModelVersionError(Exception):
    """Exception raised for unknown model versions.

    This error is thrown when an unrecognized model version is encountered.
    """

    def __init__(
        self,
        supplied_version: str,
        *args: tuple[Any, ...],
    ) -> None:
        """Initialize the exception with the supplied version.

        Args:
            supplied_version: The version of the model that was not recognized.
            *args: Additional arguments for the Exception base class.
        """
        super().__init__(args)
        self.supplied_version = supplied_version

    def __str__(self) -> str:
        """Return string representation."""
        return f"Document Version ({self.supplied_version}) of discovered file is not supported"


def _convert_language_string_type(supplied_value: dict) -> list[dict[str, str]]:
    """Convert a dictionary of language-specific strings to a list of dictionaries.

    This function takes a dictionary with language codes as keys and
    corresponding language-specific strings as values, and converts it to a list
    of dictionaries with 'languageCode' and 'languageText' keys.

    Args:
        supplied_value: A dictionary containing language codes as keys and
            language strings as values.

    Returns:
        A list of dictionaries, each containing 'languageCode' and 'languageText'
        keys, representing the converted language strings.
    """
    return [
        {
            "languageCode": "en",
            "languageText": supplied_value["en"],
        },
        {
            "languageCode": "nn",
            "languageText": supplied_value["nn"],
        },
        {
            "languageCode": "nb",
            "languageText": supplied_value["nb"],
        },
    ]


def find_and_update_language_strings(supplied_metadata: dict | None) -> dict | None:
    """Find and update language-specific strings in the supplied metadata.

    This function iterates through the supplied metadata dictionary.
    For each key-value pair, if the value is a dictionary containing "en"
    it is passed to the `_convert_language_string_type` function to potentially
    update its format.

    Args:
        supplied_metadata: A metadata dictionary where values may include nested
            dictionaries with language-specific strings.

    Returns:
        The updated metadata dictionary. If the supplied metadata is not a
        dictionary, it returns `None`.
    """
    if isinstance(supplied_metadata, dict):
        for key, value in supplied_metadata.items():
            if isinstance(value, dict) and "en" in value:
                supplied_metadata[key] = _convert_language_string_type(value)
        return supplied_metadata
    return None


def remove_element_from_model(
    supplied_metadata: dict[str, Any],
    element_to_remove: str,
) -> None:
    """Remove an element from the supplied metadata dictionary.

    This function deletes a specified element from the supplied metadata dictionary
    if it exists.

    Args:
        supplied_metadata: The metadata dictionary from which the element will be
            removed.
        element_to_remove: The key of the element to be removed from the metadata
            dictionary.
    """
    supplied_metadata.pop(element_to_remove, None)


def cast_to_date_type(value_to_update: str | None) -> str | None:
    """Convert a string to a date string in ISO format.

    This function takes a string representing a date and converts it to a
    date string in ISO format. If the input is `None`, it returns `None` without
    modification.

    Args:
        value_to_update: A string representing a date or `None`.

    Returns:
        The date string in ISO format if the input was a valid date string, or
        `None` if the input was `None`.
    """
    if value_to_update is None:
        return value_to_update

    return str(
        arrow.get(
            value_to_update,
        ).date(),
    )


def convert_is_personal_data(supplied_metadata: dict[str, Any]) -> None:
    """Convert 'is_personal_data' values in the supplied metadata to boolean.

    Iterates over variables in the supplied metadata and updates the
    'is_personal_data' field:
      - Sets it to True for NON_PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA and PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA.
      - Sets it to False for NOT_PERSONAL_DATA.

    Args:
        supplied_metadata: The metadata dictionary to be updated.
    """
    for variable in supplied_metadata[DATADOC_KEY][VARIABLES_KEY]:
        value = variable["is_personal_data"]
        if value in (
            "NON_PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA",
            "PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA",
        ):
            variable["is_personal_data"] = True
        elif value == "NOT_PERSONAL_DATA":
            variable["is_personal_data"] = False


def copy_pseudonymization_metadata(supplied_metadata: dict[str, Any]) -> None:
    """Copies pseudonymization metadata from the old pseudonymization section into the corresponding variable.

    For each variable in `supplied_metadata[DATADOC_KEY][VARIABLES_KEY]` that has a matching
    `short_name` in `supplied_metadata[PSEUDONYMIZATION_KEY]["pseudo_variables"]`, this
    function copies the following fields into the variable's 'pseudonymization' dictionary:

        - stable_identifier_type
        - stable_identifier_version
        - encryption_algorithm
        - encryption_key_reference
        - encryption_algorithm_parameters

    From the pseudo_dataset the value dataset_pseudo_time is copied to each variable as pseudonymization_time.

    Args:
        supplied_metadata: The metadata dictionary to be updated.
    """
    pseudo_vars = supplied_metadata.get(PSEUDONYMIZATION_KEY, {}).get(
        "pseudo_variables", []
    )
    pseudo_dataset = (
        supplied_metadata.get(PSEUDONYMIZATION_KEY, {}).get("pseudo_dataset") or {}
    )
    pseudo_time = pseudo_dataset.get("dataset_pseudo_time", None)
    datadoc_vars = supplied_metadata.get(DATADOC_KEY, {}).get(VARIABLES_KEY, [])
    pseudo_lookup = {var.get("short_name"): var for var in pseudo_vars}

    for variable in datadoc_vars:
        short_name = variable.get("short_name")
        if short_name in pseudo_lookup:
            pseudo_var = pseudo_lookup[short_name]
            variable[PSEUDONYMIZATION_KEY] = variable.get(
                PSEUDONYMIZATION_KEY, {}
            ).copy()

            for field in [
                "stable_identifier_type",
                "stable_identifier_version",
                "encryption_algorithm",
                "encryption_key_reference",
                "encryption_algorithm_parameters",
            ]:
                variable[PSEUDONYMIZATION_KEY][field] = pseudo_var[field]
            variable[PSEUDONYMIZATION_KEY]["pseudonymization_time"] = pseudo_time

        else:
            variable[PSEUDONYMIZATION_KEY] = None


def convert_datetime_to_date(date_value: str | None) -> str | None:
    """Convert ISO datetime string to date string, handling None and invalid values."""
    if not date_value or not isinstance(date_value, str):
        return date_value

    try:
        dt = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        return dt.date().isoformat()
    except ValueError:
        return date_value


def add_container(existing_metadata: dict) -> dict:
    """Add container for previous versions.

    Adds a container structure for previous versions of metadata.
    This function wraps the existing metadata in a new container structure
    that includes the 'document_version', 'datadoc', and 'pseudonymization'
    fields. The 'document_version' is set to "0.0.1" and 'pseudonymization'
    is set to None.

    Args:
        existing_metadata: The original metadata dictionary to be wrapped.

    Returns:
        A new dictionary containing the wrapped metadata with additional fields.
    """
    return {
        DOCUMENT_VERSION_KEY: "0.0.1",
        DATADOC_KEY: existing_metadata,
        PSEUDONYMIZATION_KEY: None,
    }


def is_metadata_in_container_structure(
    metadata: dict,
) -> bool:
    """Check if the metadata is in the container structure.

    At a certain point a metadata 'container' was introduced.
    The container provides a structure for different 'types' of metadata, such as
    'datadoc', 'pseudonymization' etc.
    This function determines if the given metadata dictionary follows this container
    structure by checking for the presence of the 'datadoc' field.

    Args:
        metadata: The metadata dictionary to check.

    Returns:
        True if the metadata is in the container structure (i.e., contains the
        'datadoc' field), False otherwise.
    """
    return DATADOC_KEY in metadata
