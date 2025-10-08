"""Code relating to merging metadata from an existing metadata document and metadata extracted from a new dataset.

This is primarily convenience functionality for users whereby they can programmatically generate metadata without
having to manually enter it. This is primarily useful when data is sharded by time (i.e. each dataset applies for
a particular period like a month or a year). Assuming there aren't structural changes, the metadata may be reused
for all periods.

It is important to be able to detect changes in the structure of the data and warn users about this so that they can
make changes as appropriate.
"""

import copy
import logging
import warnings
from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import cast

import datadoc_model
import datadoc_model.all_optional.model as all_optional_model
import datadoc_model.required.model as required_model
from cloudpathlib import CloudPath

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo
from dapla_metadata.datasets.utility.constants import (
    DATASET_FIELDS_FROM_EXISTING_METADATA,
)
from dapla_metadata.datasets.utility.constants import INCONSISTENCIES_MESSAGE
from dapla_metadata.datasets.utility.utils import OptionalDatadocMetadataType
from dapla_metadata.datasets.utility.utils import VariableListType

logger = logging.getLogger(__name__)

BUCKET_NAME_MESSAGE = "Bucket name"
DATA_PRODUCT_NAME_MESSAGE = "Data product name"
DATASET_STATE_MESSAGE = "Dataset state"
DATASET_SHORT_NAME_MESSAGE = "Dataset short name"
VARIABLES_ADDITIONAL_MESSAGE = (
    "Dataset has additional variables than defined in metadata"
)
VARIABLE_RENAME_MESSAGE = "Variables have been renamed in the dataset"
VARIABLE_ORDER_MESSAGE = "The order of variables in the dataset has changed"
VARIABLE_DATATYPES_MESSAGE = "Variable datatypes differ"
VARIABLES_FEWER_MESSAGE = "Dataset has fewer variables than defined in metadata"


class InconsistentDatasetsWarning(UserWarning):
    """Existing and new datasets differ significantly from one another."""


class InconsistentDatasetsError(ValueError):
    """Existing and new datasets differ significantly from one another."""


@dataclass
class DatasetConsistencyStatus:
    """Store the status for different aspects of dataset consistency.

    Attributes:
        message: Communicates to the user what aspect is inconsistent.
        success: False if inconsistency is detected.
        variables: Optionally communicate which variables are affected.
    """

    message: str
    success: bool
    variables: Iterable[str] = field(default_factory=list)

    def __str__(self) -> str:
        """Format the user message."""
        message = self.message
        if self.variables:
            message += f"\n\tVariables: {self.variables}"
        return message


def check_dataset_consistency(
    new_dataset_path: Path | CloudPath,
    existing_dataset_path: Path,
) -> list[DatasetConsistencyStatus]:
    """Run consistency tests.

    Args:
        new_dataset_path: Path to the dataset to be documented.
        existing_dataset_path: Path stored in the existing metadata.

    Returns:
        List of consistency check results.
    """
    new_dataset_path_info = DaplaDatasetPathInfo(new_dataset_path)
    existing_dataset_path_info = DaplaDatasetPathInfo(existing_dataset_path)
    return [
        DatasetConsistencyStatus(
            message=BUCKET_NAME_MESSAGE,
            success=(
                new_dataset_path_info.bucket_name
                == existing_dataset_path_info.bucket_name
            ),
        ),
        DatasetConsistencyStatus(
            message=DATA_PRODUCT_NAME_MESSAGE,
            success=(
                new_dataset_path_info.statistic_short_name
                == existing_dataset_path_info.statistic_short_name
            ),
        ),
        DatasetConsistencyStatus(
            message=DATASET_STATE_MESSAGE,
            success=(
                new_dataset_path_info.dataset_state
                == existing_dataset_path_info.dataset_state
            ),
        ),
        DatasetConsistencyStatus(
            message=DATASET_SHORT_NAME_MESSAGE,
            success=(
                new_dataset_path_info.dataset_short_name
                == existing_dataset_path_info.dataset_short_name
            ),
        ),
    ]


def check_variables_consistency(
    extracted_variables: VariableListType,
    existing_variables: VariableListType,
) -> list[DatasetConsistencyStatus]:
    """Check for consistency in variables structure.

    Compares the existing metadata and that extracted from the new dataset and provides
    highly detailed feedback on what is different between them.

    We don't return all the results because that could create conflicting messages and false positives.

    Args:
        extracted_variables (VariableListType): Variables extracted from the new dataset.
        existing_variables (VariableListType): Variables already documented in existing metadata

    Returns:
        list[DatasetConsistencyStatus]: The list of checks and whether they were successful.
    """
    extracted_names_set = {v.short_name or "" for v in extracted_variables}
    existing_names_set = {v.short_name or "" for v in existing_variables}
    same_length = len(extracted_variables) == len(existing_variables)
    more_extracted_variables = extracted_names_set.difference(existing_names_set)
    fewer_extracted_variables = existing_names_set.difference(extracted_names_set)
    results = []
    if same_length:
        if more_extracted_variables:
            results.append(
                DatasetConsistencyStatus(
                    message=VARIABLE_RENAME_MESSAGE,
                    variables=more_extracted_variables,
                    success=not bool(more_extracted_variables),
                )
            )
        else:
            results.append(
                DatasetConsistencyStatus(
                    message=VARIABLE_ORDER_MESSAGE,
                    success=[v.short_name or "" for v in extracted_variables]
                    == [v.short_name or "" for v in existing_variables],
                )
            )
            results.append(
                DatasetConsistencyStatus(
                    message=VARIABLE_DATATYPES_MESSAGE,
                    success=[v.data_type for v in extracted_variables]
                    == [v.data_type for v in existing_variables],
                )
            )
    else:
        results.extend(
            [
                DatasetConsistencyStatus(
                    message=VARIABLES_ADDITIONAL_MESSAGE,
                    variables=more_extracted_variables,
                    success=not bool(more_extracted_variables),
                ),
                DatasetConsistencyStatus(
                    message=VARIABLES_FEWER_MESSAGE,
                    variables=fewer_extracted_variables,
                    success=not bool(fewer_extracted_variables),
                ),
            ]
        )
    return results


def check_ready_to_merge(
    results: list[DatasetConsistencyStatus], *, errors_as_warnings: bool
) -> None:
    """Check if the datasets are consistent enough to make a successful merge of metadata.

    Args:
        results: List if dict with property name and boolean success flag
        errors_as_warnings: True if failing checks should be raised as warnings, not errors.

    Raises:
        InconsistentDatasetsError: If inconsistencies are found and `errors_as_warnings == False`
    """
    if failures := [result for result in results if not result.success]:
        messages_list = "\n - ".join(str(f) for f in failures)
        msg = f"{INCONSISTENCIES_MESSAGE}\n - {messages_list}"
        if errors_as_warnings:
            warnings.warn(
                message=msg,
                category=InconsistentDatasetsWarning,
                stacklevel=2,
            )
        else:
            raise InconsistentDatasetsError(
                msg,
            )


def override_dataset_fields(
    merged_metadata: all_optional_model.DatadocMetadata,
    existing_metadata: all_optional_model.DatadocMetadata
    | required_model.DatadocMetadata,
) -> None:
    """Overrides specific fields in the dataset of `merged_metadata` with values from the dataset of `existing_metadata`.

    This function iterates over a predefined list of fields, `DATASET_FIELDS_FROM_EXISTING_METADATA`,
    and sets the corresponding fields in the `merged_metadata.dataset` object to the values
    from the `existing_metadata.dataset` object.

    Args:
        merged_metadata: An instance of `DatadocMetadata` containing the dataset to be updated.
        existing_metadata: An instance of `DatadocMetadata` containing the dataset whose values are used to update `merged_metadata.dataset`.

    Returns:
        `None`.
    """
    if merged_metadata.dataset and existing_metadata.dataset:
        # Override the fields as defined
        for field in DATASET_FIELDS_FROM_EXISTING_METADATA:
            setattr(
                merged_metadata.dataset,
                field,
                getattr(existing_metadata.dataset, field),
            )


def merge_variables(
    existing_metadata: OptionalDatadocMetadataType,
    extracted_metadata: all_optional_model.DatadocMetadata,
    merged_metadata: all_optional_model.DatadocMetadata,
) -> all_optional_model.DatadocMetadata:
    """Merges variables from the extracted metadata into the existing metadata and updates the merged metadata.

    This function compares the variables from `extracted_metadata` with those in `existing_metadata`.
    For each variable in `extracted_metadata`, it checks if a variable with the same `short_name` exists
    in `existing_metadata`. If a match is found, it updates the existing variable with information from
    `extracted_metadata`. If no match is found, the variable from `extracted_metadata` is directly added to `merged_metadata`.

    Args:
        existing_metadata: The metadata object containing the current state of variables.
        extracted_metadata: The metadata object containing new or updated variables to merge.
        merged_metadata: The metadata object that will contain the result of the merge.

    Returns:
        all_optional_model.DatadocMetadata: The `merged_metadata` object containing variables from both `existing_metadata`
        and `extracted_metadata`.
    """
    if (
        existing_metadata is not None
        and existing_metadata.variables is not None
        and extracted_metadata is not None
        and extracted_metadata.variables is not None
        and merged_metadata.variables is not None
    ):
        for extracted in extracted_metadata.variables:
            existing = next(
                (
                    existing
                    for existing in existing_metadata.variables
                    if existing.short_name == extracted.short_name
                ),
                None,
            )
            if existing:
                existing.id = (
                    None  # Set to None so that it will be set assigned a fresh ID later
                )
                existing.contains_data_from = (
                    extracted.contains_data_from or existing.contains_data_from
                )
                existing.contains_data_until = (
                    extracted.contains_data_until or existing.contains_data_until
                )
                merged_metadata.variables.append(
                    cast("datadoc_model.all_optional.model.Variable", existing)
                )
            else:
                # If there is no existing metadata for this variable, we just use what we have extracted
                merged_metadata.variables.append(extracted)
    return merged_metadata


def merge_metadata(
    extracted_metadata: all_optional_model.DatadocMetadata | None,
    existing_metadata: OptionalDatadocMetadataType,
) -> all_optional_model.DatadocMetadata:
    if not existing_metadata:
        logger.warning(
            "No existing metadata found, no merge to perform. Continuing with extracted metadata.",
        )
        return extracted_metadata or all_optional_model.DatadocMetadata()

    if not extracted_metadata:
        return cast("all_optional_model.DatadocMetadata", existing_metadata)

    # Use the extracted metadata as a base
    merged_metadata = all_optional_model.DatadocMetadata(
        dataset=copy.deepcopy(extracted_metadata.dataset),
        variables=[],
    )

    override_dataset_fields(
        merged_metadata=merged_metadata,
        existing_metadata=existing_metadata,
    )

    # Merge variables.
    # For each extracted variable, copy existing metadata into the merged metadata
    return merge_variables(
        existing_metadata=existing_metadata,
        extracted_metadata=extracted_metadata,
        merged_metadata=merged_metadata,
    )
