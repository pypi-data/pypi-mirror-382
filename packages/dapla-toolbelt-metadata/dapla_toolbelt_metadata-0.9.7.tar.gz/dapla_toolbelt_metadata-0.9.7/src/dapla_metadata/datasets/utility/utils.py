from __future__ import annotations

import datetime  # import is needed in xdoctest
import logging
import pathlib
import uuid
from typing import Any
from typing import TypeAlias

import datadoc_model.all_optional.model as all_optional_model
import datadoc_model.required.model as required_model
import google.auth
from cloudpathlib import CloudPath
from cloudpathlib import GSClient
from cloudpathlib import GSPath
from datadoc_model.all_optional.model import Assessment
from datadoc_model.all_optional.model import DataSetState
from datadoc_model.all_optional.model import VariableRole

from dapla_metadata.dapla import user_info
from dapla_metadata.datasets.utility.constants import DAEAD_ENCRYPTION_KEY_REFERENCE
from dapla_metadata.datasets.utility.constants import ENCRYPTION_PARAMETER_KEY_ID
from dapla_metadata.datasets.utility.constants import ENCRYPTION_PARAMETER_SNAPSHOT_DATE
from dapla_metadata.datasets.utility.constants import ENCRYPTION_PARAMETER_STRATEGY
from dapla_metadata.datasets.utility.constants import ENCRYPTION_PARAMETER_STRATEGY_SKIP
from dapla_metadata.datasets.utility.constants import NUM_OBLIGATORY_VARIABLES_FIELDS
from dapla_metadata.datasets.utility.constants import (
    OBLIGATORY_DATASET_METADATA_IDENTIFIERS,
)
from dapla_metadata.datasets.utility.constants import (
    OBLIGATORY_DATASET_METADATA_IDENTIFIERS_MULTILANGUAGE,
)
from dapla_metadata.datasets.utility.constants import (
    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS,
)
from dapla_metadata.datasets.utility.constants import (
    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE,
)
from dapla_metadata.datasets.utility.constants import (
    OBLIGATORY_VARIABLES_PSEUDONYMIZATION_IDENTIFIERS,
)
from dapla_metadata.datasets.utility.constants import PAPIS_ENCRYPTION_KEY_REFERENCE
from dapla_metadata.datasets.utility.constants import PAPIS_STABLE_IDENTIFIER_TYPE
from dapla_metadata.datasets.utility.enums import EncryptionAlgorithm

logger = logging.getLogger(__name__)

DatadocMetadataType: TypeAlias = (
    all_optional_model.DatadocMetadata | required_model.DatadocMetadata
)
DatasetType: TypeAlias = all_optional_model.Dataset | required_model.Dataset
VariableType: TypeAlias = all_optional_model.Variable | required_model.Variable
PseudonymizationType: TypeAlias = (
    all_optional_model.Pseudonymization | required_model.Pseudonymization
)
VariableListType: TypeAlias = (
    list[all_optional_model.Variable] | list[required_model.Variable]
)
OptionalDatadocMetadataType: TypeAlias = DatadocMetadataType | None


def get_current_date() -> str:
    """Return a current date as str."""
    return datetime.datetime.now(tz=datetime.timezone.utc).date().isoformat()


def get_timestamp_now() -> datetime.datetime:
    """Return a timestamp for the current moment."""
    return datetime.datetime.now(tz=datetime.timezone.utc)


def normalize_path(path: str) -> pathlib.Path | CloudPath:
    """Obtain a pathlib compatible Path.

    Obtains a pathlib compatible Path regardless of whether the file is on a filesystem or in GCS.

    Args:
        path: Path on a filesystem or in cloud storage.

    Returns:
        Pathlib compatible object.
    """
    if path.startswith(GSPath.cloud_prefix):
        client = GSClient(credentials=google.auth.default()[0])
        return GSPath(path, client=client)
    return pathlib.Path(path)


def calculate_percentage(completed: int, total: int) -> int:
    """Calculate percentage as a rounded integer.

    Args:
        completed: The number of completed items.
        total: The total number of items.

    Returns:
        The rounded percentage of completed items out of the total.
    """
    return round((completed / total) * 100)


def derive_assessment_from_state(state: DataSetState) -> Assessment:
    """Derive assessment from dataset state.

    Args:
        state: The state of the dataset.

    Returns:
        The derived assessment of the dataset.
    """
    match state:
        case (
            DataSetState.INPUT_DATA
            | DataSetState.PROCESSED_DATA
            | DataSetState.STATISTICS
        ):
            return Assessment.PROTECTED
        case DataSetState.OUTPUT_DATA:
            return Assessment.OPEN
        case DataSetState.SOURCE_DATA:
            return Assessment.SENSITIVE


def set_default_values_variables(variables: VariableListType) -> None:
    """Set default values on variables.

    Args:
        variables: A list of variable objects to set default values on.

    Example:
        >>> variables = [all_optional_model.Variable(short_name="pers",id=None, is_personal_data = None), all_optional_model.Variable(short_name="fnr",id='9662875c-c245-41de-b667-12ad2091a1ee', is_personal_data=True)]
        >>> set_default_values_variables(variables)
        >>> isinstance(variables[0].id, uuid.UUID)
        True

        >>> variables[1].is_personal_data == True
        True

        >>> variables[0].is_personal_data == False
        True
    """
    for v in variables:
        if v.id is None:
            v.id = uuid.uuid4()
        if v.is_personal_data is None:
            v.is_personal_data = False
        if v.variable_role is None:
            v.variable_role = VariableRole.MEASURE


def set_default_values_dataset(
    dataset: DatasetType,
) -> None:
    """Set default values on dataset.

    Args:
        dataset: The dataset object to set default values on.

    Example:
        >>> dataset = all_optional_model.Dataset(id=None)
        >>> set_default_values_dataset(dataset)
        >>> dataset.id is not None
        True
    """
    if not dataset.id:
        dataset.id = uuid.uuid4()


def set_dataset_owner(
    dataset: DatasetType,
) -> None:
    """Sets the owner of the dataset from the DAPLA_GROUP_CONTEXT enviornment variable.

    Args:
        dataset: The dataset object to set default values on.
    """
    try:
        dataset.owner = user_info.get_user_info_for_current_platform().current_team
    except OSError:
        logger.exception("Failed to find environment variable DAPLA_GROUP_CONTEXT")


def set_variables_inherit_from_dataset(
    dataset: DatasetType,
    variables: list,
) -> None:
    """Set specific dataset values on a list of variable objects.

    This function populates 'data source', 'temporality type', 'contains data from',
    and 'contains data until' fields in each variable if they are not set (None).
    The values are inherited from the corresponding fields in the dataset.

    Args:
        dataset: The dataset object from which to inherit values.
        variables: A list of variable objects to update with dataset values.

    Example:
        >>> dataset = all_optional_model.Dataset(short_name='person_data_v1', id='9662875c-c245-41de-b667-12ad2091a1ee', contains_data_from="2010-09-05", contains_data_until="2022-09-05")
        >>> variables = [all_optional_model.Variable(short_name="pers", data_source=None, temporality_type=None, contains_data_from=None, contains_data_until=None)]
        >>> set_variables_inherit_from_dataset(dataset, variables)

        >>> variables[0].contains_data_from == dataset.contains_data_from
        True

        >>> variables[0].contains_data_until == dataset.contains_data_until
        True
    """
    for v in variables:
        v.contains_data_from = v.contains_data_from or dataset.contains_data_from
        v.contains_data_until = v.contains_data_until or dataset.contains_data_until


def incorrect_date_order(
    date_from: datetime.date | None,
    date_until: datetime.date | None,
) -> bool:
    """Evaluate the chronological order of two dates.

    This function checks if 'date until' is earlier than 'date from'. If so, it
    indicates an incorrect date order.

    Args:
        date_from: The start date of the time period.
        date_until: The end date of the time period.

    Returns:
        True if 'date_until' is earlier than 'date_from' or if only 'date_from' is None, False otherwise.

    Example:
        >>> incorrect_date_order(datetime.date(1980, 1, 1), datetime.date(1967, 1, 1))
        True

        >>> incorrect_date_order(datetime.date(1967, 1, 1), datetime.date(1980, 1, 1))
        False

        >>> incorrect_date_order(None, datetime.date(2024,7,1))
        True
    """
    if date_from is None and date_until is not None:
        return True
    return date_from is not None and date_until is not None and date_until < date_from


def _is_missing_multilanguage_value(
    field_name: str,
    field_value,  # noqa: ANN001 Skip type hint to enable dynamically handling value for LanguageStringType not indexable
    obligatory_list: list,
) -> bool:
    """Check obligatory fields with multilanguage value.

    This function checks whether a given field, which is supposed to have
    multilanguage values, is missing values in all specified languages.

    Args:
        field_name: The name of the field to check.
        field_value: The value of the field. Expected to be of type LanguageStringType.
        obligatory_list: A list of obligatory field names that should have multilanguage values.

    Returns:
        True if no value in any of languages for one field, False otherwise.
    """
    return bool(
        field_name in obligatory_list
        and field_value
        and (
            len(field_value[0]) > 0
            and not field_value[0]["languageText"]
            and (len(field_value) <= 1 or not field_value[1]["languageText"])
            and (len(field_value) <= 2 or not field_value[2]["languageText"])
        ),
    )


def _is_missing_metadata(
    field_name: str,
    field_value,  # noqa: ANN001 Skip type hint because method '_is_missing_multilanguage_value'
    obligatory_list: list,
    obligatory_multi_language_list: list,
) -> bool:
    """Check if an obligatory field is missing its value.

    This function checks whether a given field, which may be a simple string or a
    multilanguage value, is missing its value. It considers two lists: one for
    obligatory fields and another for obligatory multilanguage fields.

    Args:
        field_name: The name of the field to check.
        field_value: The value of the field. Can be of type str, or LanguageStringType for
            multilanguage fields.
        obligatory_list: List of obligatory fields.
        obligatory_multi_language_list: List of obligatory fields with multilanguage
            values.

    Returns:
        True if the field doesn't have a value, False otherwise.
    """
    return bool(
        (field_name in obligatory_list and field_value is None)
        or _is_missing_multilanguage_value(
            field_name,
            field_value,
            obligatory_multi_language_list,
        ),
    )


def num_obligatory_dataset_fields_completed(
    dataset: DatasetType,
) -> int:
    """Count the number of completed obligatory dataset fields.

    This function returns the total count of obligatory fields in the dataset that
    have values (are not None).

    Args:
        dataset: The dataset object for which to count the fields.

    Returns:
        The number of obligatory dataset fields that have been completed (not None).
    """
    return len(OBLIGATORY_DATASET_METADATA_IDENTIFIERS) - len(
        get_missing_obligatory_dataset_fields(dataset),
    )


def num_obligatory_variables_fields_completed(variables: list) -> int:
    """Count the number of obligatory fields completed for all variables.

    This function calculates the total number of obligatory fields that have
    values (are not None) for one variable in the list.

    Args:
        variables: A list with variable objects.

    Returns:
        The total number of obligatory variable fields that have been completed
        (not None) for all variables.
    """
    num_completed = 0
    for v in variables:
        num_completed += num_obligatory_variable_fields_completed(v)
    return num_completed


def num_obligatory_variable_fields_completed(
    variable: all_optional_model.Variable,
) -> int:
    """Count the number of obligatory fields completed for one variable.

    This function calculates the total number of obligatory fields that have
    values (are not None) for one variable in the list.

    Args:
        variable: The variable to count obligatory fields for.

    Returns:
        The total number of obligatory variable fields that have been completed
        (not None) for one variable.
    """
    missing_metadata = [
        key
        for key, value in variable.model_dump().items()
        if _is_missing_metadata(
            key,
            value,
            OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS,
            OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE,
        )
    ]
    return NUM_OBLIGATORY_VARIABLES_FIELDS - len(missing_metadata)


def num_obligatory_pseudo_fields_missing(
    variables: list[all_optional_model.Variable],
) -> int:
    """Counts the number of obligatory pseudonymization fields are missing.

    Args:
        variables: The variables to count obligatory fields for.

    Returns:
        The number of obligatory pseudonymization fields that are missing.
    """
    return sum(
        getattr(v.pseudonymization, field, None) is None
        for v in variables
        if v.pseudonymization is not None
        for field in OBLIGATORY_VARIABLES_PSEUDONYMIZATION_IDENTIFIERS
    )


def get_missing_obligatory_dataset_fields(
    dataset: DatasetType,
) -> list:
    """Identify all obligatory dataset fields that are missing values.

    This function checks for obligatory fields that are either directly missing
    (i.e., set to `None`) or have multilanguage values with empty content.

    Args:
        dataset: The dataset object to examine. This object must support the
            `model_dump()` method which returns a dictionary of field names and
            values.

    Returns:
        A list of field names (as strings) that are missing values. This includes:
            - Fields that are directly `None` and are listed as obligatory metadata.
            - Multilanguage fields (listed as obligatory metadata`) where
            the value exists but the primary language text is empty.
    """
    return [
        key
        for key, value in dataset.model_dump().items()
        if _is_missing_metadata(
            key,
            value,
            OBLIGATORY_DATASET_METADATA_IDENTIFIERS,
            OBLIGATORY_DATASET_METADATA_IDENTIFIERS_MULTILANGUAGE,
        )
    ]


def get_missing_obligatory_variables_fields(variables: list) -> list[dict]:
    """Identify obligatory variable fields that are missing values for each variable.

    This function checks for obligatory fields that are either directly missing
    (i.e., set to `None`) or have multilanguage values with empty content.

    Args:
        variables: A list of variable objects to check for missing obligatory fields.

    Returns:
        A list of dictionaries with variable short names as keys and list of missing
        obligatory variable fields as values. This includes:
            - Fields that are directly `None` and are llisted as obligatory metadata.
            - Multilanguage fields (listed as obligatory metadata) where the value
            exists but the primary language text is empty.
    """
    missing_variables_fields = [
        {
            variable.short_name: [
                key
                for key, value in variable.model_dump().items()
                if _is_missing_metadata(
                    key,
                    value,
                    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS,
                    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE,
                )
            ],
        }
        for variable in variables
    ]
    # Filtering out variable keys with empty values list
    return [item for item in missing_variables_fields if next(iter(item.values()))]


def get_missing_obligatory_variables_pseudo_fields(
    variables: list[all_optional_model.Variable],
) -> list[dict]:
    """Identify obligatory variable pseudonymization fields that are missing values for each variable.

    This function checks for obligatory fields that are directly missing
    (i.e., set to `None`).

    Args:
        variables: A list of variable objects to check for missing obligatory pseudonymization fields.

    Returns:
        A list of dictionaries with variable short names as keys and list of missing
        obligatory variable pseudonymization fields as values. This includes:
            - Fields that are directly `None` and are listed as obligatory metadata.
    """
    return [
        {
            v.short_name: [
                key
                for key, value in v.pseudonymization.model_dump().items()
                if _is_missing_metadata(
                    key,
                    value,
                    OBLIGATORY_VARIABLES_PSEUDONYMIZATION_IDENTIFIERS,
                    [],
                )
            ]
        }
        for v in variables
        if v.pseudonymization is not None
    ]


def running_in_notebook() -> bool:
    """Return True if running in Jupyter Notebook."""
    try:
        return bool(get_ipython().__class__.__name__ == "ZMQInteractiveShell")  # type: ignore [name-defined]
    except NameError:
        # The get_ipython method is globally available in ipython interpreters
        # as used in Jupyter. However it is not available in other python
        # interpreters and will throw a NameError. Therefore we're not running
        # in Jupyter.
        return False


def _ensure_encryption_parameters(
    existing: list[dict[str, Any]] | None,
    required: dict[str, Any],
) -> list[dict[str, Any]]:
    """Ensure required key/value pairs exist in parameters list."""
    result = list(existing or [])

    # Ensure each required key is present in at least one dict
    for key, value in required.items():
        if not any(key in d for d in result):
            result.append({key: value})

    return result


def set_default_values_pseudonymization(
    variable: VariableType,
    pseudonymization: PseudonymizationType | None,
) -> None:
    """Populate pseudonymization fields with defaults based on the encryption algorithm.

    Updates the encryption key reference and encryption parameters if they are not set,
    handling both PAPIS and DAED algorithms. Leaves unknown algorithms unchanged.
    """
    if pseudonymization is None:
        return
    if variable.pseudonymization is None:
        variable.pseudonymization = pseudonymization
    match pseudonymization.encryption_algorithm:
        case EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value:
            if not pseudonymization.encryption_key_reference:
                pseudonymization.encryption_key_reference = (
                    PAPIS_ENCRYPTION_KEY_REFERENCE
                )
            base_params = {
                ENCRYPTION_PARAMETER_KEY_ID: PAPIS_ENCRYPTION_KEY_REFERENCE,
                ENCRYPTION_PARAMETER_STRATEGY: ENCRYPTION_PARAMETER_STRATEGY_SKIP,
            }
            if pseudonymization.stable_identifier_type == PAPIS_STABLE_IDENTIFIER_TYPE:
                base_params[ENCRYPTION_PARAMETER_SNAPSHOT_DATE] = get_current_date()
            pseudonymization.encryption_algorithm_parameters = (
                _ensure_encryption_parameters(
                    pseudonymization.encryption_algorithm_parameters,
                    base_params,
                )
            )
        case EncryptionAlgorithm.DAEAD_ENCRYPTION_ALGORITHM.value:
            if not pseudonymization.encryption_key_reference:
                pseudonymization.encryption_key_reference = (
                    DAEAD_ENCRYPTION_KEY_REFERENCE
                )
            pseudonymization.encryption_algorithm_parameters = (
                _ensure_encryption_parameters(
                    pseudonymization.encryption_algorithm_parameters,
                    {
                        ENCRYPTION_PARAMETER_KEY_ID: DAEAD_ENCRYPTION_KEY_REFERENCE,
                    },
                )
            )
        case _:
            pass
