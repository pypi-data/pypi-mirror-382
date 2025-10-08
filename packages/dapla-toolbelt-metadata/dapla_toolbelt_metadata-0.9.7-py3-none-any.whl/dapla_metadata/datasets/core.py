"""Handle reading, updating and writing of metadata."""

from __future__ import annotations

import copy
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING
from typing import cast

import datadoc_model.all_optional.model as all_optional_model
import datadoc_model.required.model as required_model
from datadoc_model.all_optional.model import DataSetStatus

from dapla_metadata._shared import config
from dapla_metadata.dapla import user_info
from dapla_metadata.datasets._merge import DatasetConsistencyStatus
from dapla_metadata.datasets._merge import check_dataset_consistency
from dapla_metadata.datasets._merge import check_ready_to_merge
from dapla_metadata.datasets._merge import check_variables_consistency
from dapla_metadata.datasets._merge import merge_metadata
from dapla_metadata.datasets.compatibility import is_metadata_in_container_structure
from dapla_metadata.datasets.compatibility import upgrade_metadata
from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo
from dapla_metadata.datasets.dataset_parser import DatasetParser
from dapla_metadata.datasets.model_validation import ValidateDatadocMetadata
from dapla_metadata.datasets.statistic_subject_mapping import StatisticSubjectMapping
from dapla_metadata.datasets.utility.constants import (
    DEFAULT_SPATIAL_COVERAGE_DESCRIPTION,
)
from dapla_metadata.datasets.utility.constants import METADATA_DOCUMENT_FILE_SUFFIX
from dapla_metadata.datasets.utility.constants import NUM_OBLIGATORY_DATASET_FIELDS
from dapla_metadata.datasets.utility.constants import NUM_OBLIGATORY_VARIABLES_FIELDS
from dapla_metadata.datasets.utility.urn import convert_uris_to_urns
from dapla_metadata.datasets.utility.urn import klass_urn_converter
from dapla_metadata.datasets.utility.urn import vardef_urn_converter
from dapla_metadata.datasets.utility.utils import OptionalDatadocMetadataType
from dapla_metadata.datasets.utility.utils import VariableListType
from dapla_metadata.datasets.utility.utils import VariableType
from dapla_metadata.datasets.utility.utils import calculate_percentage
from dapla_metadata.datasets.utility.utils import derive_assessment_from_state
from dapla_metadata.datasets.utility.utils import get_timestamp_now
from dapla_metadata.datasets.utility.utils import normalize_path
from dapla_metadata.datasets.utility.utils import (
    num_obligatory_dataset_fields_completed,
)
from dapla_metadata.datasets.utility.utils import (
    num_obligatory_variables_fields_completed,
)
from dapla_metadata.datasets.utility.utils import set_dataset_owner
from dapla_metadata.datasets.utility.utils import set_default_values_dataset
from dapla_metadata.datasets.utility.utils import set_default_values_pseudonymization
from dapla_metadata.datasets.utility.utils import set_default_values_variables

if TYPE_CHECKING:
    import pathlib
    from datetime import datetime

    from cloudpathlib import CloudPath

logger = logging.getLogger(__name__)


class Datadoc:
    """Handle reading, updating and writing of metadata.

    If a metadata document exists, it is this information that is loaded. Nothing
    is inferred from the dataset. If only a dataset path is supplied the metadata
    document path is build based on the dataset path.

    Example: /path/to/dataset.parquet -> /path/to/dataset__DOC.json

    Attributes:
        dataset_path: A file path to the path to where the dataset is stored.
        metadata_document_path: A path to a metadata document if it exists.
        statistic_subject_mapping: An instance of StatisticSubjectMapping.
    """

    def __init__(
        self,
        dataset_path: str | None = None,
        metadata_document_path: str | None = None,
        statistic_subject_mapping: StatisticSubjectMapping | None = None,
        errors_as_warnings: bool = False,
        validate_required_fields_on_existing_metadata: bool = False,
    ) -> None:
        """Initialize the Datadoc instance.

        If a dataset path is supplied, it attempts to locate and load the
        corresponding metadata document. If no dataset path is provided, the class
        is instantiated without loading any metadata.

        Args:
            dataset_path: The file path to the dataset. Defaults to None.
            metadata_document_path: The file path to the metadata document.
                Defaults to None.
            statistic_subject_mapping: An instance of StatisticSubjectMapping.
                Defaults to None
            errors_as_warnings: Disable raising exceptions if inconsistencies
                are found between existing and extracted metadata.
            validate_required_fields_on_existing_metadata: Use a Pydantic model
                which validates whether required fields are present when reading
                in an existing metadata file.
        """
        self._statistic_subject_mapping = statistic_subject_mapping
        self.errors_as_warnings = errors_as_warnings
        self.validate_required_fields_on_existing_metadata = (
            validate_required_fields_on_existing_metadata
        )
        self.metadata_document: pathlib.Path | CloudPath | None = None
        self.container: all_optional_model.MetadataContainer | None = None
        self.dataset_path: pathlib.Path | CloudPath | None = None
        self.dataset = all_optional_model.Dataset()
        self.variables: VariableListType = []
        self.variables_lookup: dict[str, VariableType] = {}
        self.explicitly_defined_metadata_document = False
        self.dataset_consistency_status: list[DatasetConsistencyStatus] = []
        if metadata_document_path:
            self.metadata_document = normalize_path(metadata_document_path)
            self.explicitly_defined_metadata_document = True
            if not self.metadata_document.exists():
                msg = f"Metadata document does not exist! Provided path: {self.metadata_document}"
                raise ValueError(
                    msg,
                )
        if dataset_path:
            self.dataset_path = normalize_path(dataset_path)
            if not metadata_document_path:
                self.metadata_document = self.build_metadata_document_path(
                    self.dataset_path,
                )
        if metadata_document_path or dataset_path:
            self._extract_metadata_from_files()

    def _extract_metadata_from_files(self) -> None:
        """Read metadata from an existing metadata document or create one.

        If a metadata document exists, it reads and extracts metadata from it.
        If no metadata document is found, it creates metadata from scratch by
        extracting information from the dataset file.

        This method ensures that:
        - Metadata is extracted from an existing document if available.
        - If metadata is not available, it is extracted from the dataset file.
        - The dataset ID is set if not already present.
        - Default values are set for variables, particularly the variable role on
            creation.
        - Default values for variables ID and 'is_personal_data' are set if the
            values are None.
        - The 'contains_personal_data' attribute is set to False if not specified.
        - A lookup dictionary for variables is created based on their short names.
        """
        extracted_metadata: all_optional_model.DatadocMetadata | None = None
        existing_metadata: OptionalDatadocMetadataType = None

        if self.metadata_document and self.metadata_document.exists():
            existing_metadata = self._extract_metadata_from_existing_document(
                self.metadata_document,
            )

        if (
            self.dataset_path is not None
            and self.dataset == all_optional_model.Dataset()
            and len(self.variables) == 0
        ):
            extracted_metadata = self._extract_metadata_from_dataset(self.dataset_path)

        if (
            self.dataset_path
            and self.metadata_document
            and extracted_metadata
            and existing_metadata
        ):
            self.dataset_consistency_status = check_dataset_consistency(
                self.dataset_path,
                Path(self.metadata_document),
            )
            self.dataset_consistency_status.extend(
                check_variables_consistency(
                    extracted_metadata.variables or [],
                    existing_metadata.variables or [],
                )
            )

        if (
            self.dataset_path
            and self.explicitly_defined_metadata_document
            and self.metadata_document is not None
            and self.metadata_document.exists()
            and extracted_metadata is not None
            and existing_metadata is not None
        ):
            check_ready_to_merge(
                self.dataset_consistency_status,
                errors_as_warnings=self.errors_as_warnings,
            )
            merged_metadata = merge_metadata(
                extracted_metadata,
                existing_metadata,
            )
            # We need to override this so that the document gets saved to the correct
            # location, otherwise we would overwrite the existing document!
            self.metadata_document = self.build_metadata_document_path(
                self.dataset_path,
            )
            self._set_metadata(merged_metadata)
        else:
            self._set_metadata(existing_metadata or extracted_metadata)

    def _set_metadata(
        self,
        metadata: OptionalDatadocMetadataType,
    ) -> None:
        if not metadata or not (metadata.dataset and metadata.variables):
            msg = "Could not read metadata"
            raise ValueError(msg)
        self.dataset = cast("all_optional_model.Dataset", metadata.dataset)
        self.variables = metadata.variables

        set_default_values_variables(self.variables)
        set_default_values_dataset(cast("all_optional_model.Dataset", self.dataset))
        set_dataset_owner(self.dataset)
        convert_uris_to_urns(self.variables, "definition_uri", [vardef_urn_converter])
        convert_uris_to_urns(
            self.variables, "classification_uri", [klass_urn_converter]
        )
        self._create_variables_lookup()

    def _create_variables_lookup(self) -> None:
        self.variables_lookup = {
            v.short_name: v for v in self.variables if v.short_name
        }

    def _extract_metadata_from_existing_document(
        self,
        document: pathlib.Path | CloudPath,
    ) -> OptionalDatadocMetadataType:
        """Read metadata from an existing metadata document.

        If an existing metadata document is available, this method reads and
        loads the metadata from it. It validates and upgrades the metadata as
        necessary. If we have read in a file with an empty "datadoc" structure
        the process ends.
        A typical example causing a empty datadoc is a file produced from a
        pseudonymization process.

        Args:
            document: A path to the existing metadata document.

        Raises:
            json.JSONDecodeError: If the metadata document cannot be parsed.
            pydantic.ValidationError: If the data does not successfully validate.
        """
        metadata_model = (
            required_model
            if self.validate_required_fields_on_existing_metadata
            else all_optional_model
        )
        fresh_metadata = {}
        try:
            with document.open(mode="r", encoding="utf-8") as file:
                fresh_metadata = json.load(file)
            logger.info("Opened existing metadata file %s", document)
            fresh_metadata = upgrade_metadata(
                fresh_metadata,
            )
            if is_metadata_in_container_structure(fresh_metadata):
                self.container = metadata_model.MetadataContainer.model_validate_json(
                    json.dumps(fresh_metadata),
                )
                datadoc_metadata = fresh_metadata["datadoc"]
            else:
                datadoc_metadata = fresh_metadata
            if datadoc_metadata is None:
                return None
            return metadata_model.DatadocMetadata.model_validate_json(
                json.dumps(datadoc_metadata),
            )
        except json.JSONDecodeError:
            logger.warning(
                "Could not open existing metadata file %s. \
                    Falling back to collecting data from the dataset",
                document,
                exc_info=True,
            )
            return None

    def _extract_subject_field_from_path(
        self,
        dapla_dataset_path_info: DaplaDatasetPathInfo,
    ) -> str | None:
        """Extract the statistic short name from the dataset file path.

        Map the extracted statistic short name to its corresponding statistical
        subject.

        Args:
            dapla_dataset_path_info: The object representing the decomposed file
                path.

        Returns:
            The code for the statistical subject or None if we couldn't map to one.
        """
        if self._statistic_subject_mapping is None:
            with ThreadPoolExecutor(max_workers=12) as executor:
                return StatisticSubjectMapping(
                    executor,
                    config.get_statistical_subject_source_url(),
                ).get_secondary_subject(
                    dapla_dataset_path_info.statistic_short_name,
                )
        else:
            return self._statistic_subject_mapping.get_secondary_subject(
                dapla_dataset_path_info.statistic_short_name,
            )

    def _extract_metadata_from_dataset(
        self,
        dataset: pathlib.Path | CloudPath,
    ) -> all_optional_model.DatadocMetadata:
        """Obtain what metadata we can from the dataset itself.

        This makes it easier for the user by 'pre-filling' certain fields.
        Certain elements are dependent on the dataset being saved according
        to SSB's standard.

        Args:
            dataset: The path to the dataset file, which can be a local or
                cloud path.

        Side Effects:
            Updates the following instance attributes:
                - ds_schema: An instance of DatasetParser initialized for the
                    given dataset file.
                - dataset: An instance of model.Dataset with pre-filled metadata
                    fields.
                - variables: A list of fields extracted from the dataset schema.
        """
        dapla_dataset_path_info = DaplaDatasetPathInfo(dataset)
        metadata = all_optional_model.DatadocMetadata()

        metadata.dataset = all_optional_model.Dataset(
            short_name=dapla_dataset_path_info.dataset_short_name,
            dataset_state=dapla_dataset_path_info.dataset_state,
            dataset_status=DataSetStatus.DRAFT,
            assessment=(
                derive_assessment_from_state(
                    dapla_dataset_path_info.dataset_state,
                )
                if dapla_dataset_path_info.dataset_state is not None
                else None
            ),
            version=dapla_dataset_path_info.dataset_version,
            contains_data_from=dapla_dataset_path_info.contains_data_from,
            contains_data_until=dapla_dataset_path_info.contains_data_until,
            file_path=str(self.dataset_path),
            metadata_created_by=user_info.get_user_info_for_current_platform().short_email,
            subject_field=self._extract_subject_field_from_path(
                dapla_dataset_path_info,
            ),
            spatial_coverage_description=DEFAULT_SPATIAL_COVERAGE_DESCRIPTION,
        )
        metadata.variables = DatasetParser.for_file(dataset).get_fields()
        return metadata

    @staticmethod
    def build_metadata_document_path(
        dataset_path: pathlib.Path | CloudPath,
    ) -> pathlib.Path | CloudPath:
        """Build the path to the metadata document corresponding to the given dataset.

        Args:
            dataset_path: Path to the dataset we wish to create metadata for.
        """
        return dataset_path.parent / (dataset_path.stem + METADATA_DOCUMENT_FILE_SUFFIX)

    def datadoc_model(self) -> all_optional_model.MetadataContainer:
        """Return the underlying datadoc model."""
        datadoc: ValidateDatadocMetadata = ValidateDatadocMetadata(
            percentage_complete=self.percent_complete,
            dataset=self.dataset,
            variables=self.variables,
        )
        if self.container:
            res = copy.deepcopy(self.container)
            res.datadoc = datadoc
            return res
        return all_optional_model.MetadataContainer(datadoc=datadoc)

    def write_metadata_document(self) -> None:
        """Write all currently known metadata to file.

        Side Effects:
            - Updates the dataset's metadata_last_updated_date and
                metadata_last_updated_by attributes.
            - Updates the dataset's file_path attribute.
            - Validates the metadata model and stores it in a MetadataContainer.
            - Writes the validated metadata to a file if the metadata_document
                attribute is set.
            - Logs the action and the content of the metadata document.

        Raises:
            ValueError: If no metadata document is specified for saving.
        """
        timestamp: datetime = get_timestamp_now()
        self.dataset.metadata_last_updated_date = timestamp
        self.dataset.metadata_last_updated_by = (
            user_info.get_user_info_for_current_platform().short_email
        )
        self.dataset.file_path = str(self.dataset_path)
        datadoc: ValidateDatadocMetadata = ValidateDatadocMetadata(
            percentage_complete=self.percent_complete,
            dataset=self.dataset,
            variables=self.variables,
        )
        if self.container:
            self.container.datadoc = datadoc
        else:
            self.container = all_optional_model.MetadataContainer(datadoc=datadoc)
        if self.metadata_document:
            content = self.container.model_dump_json(indent=4)
            self.metadata_document.write_text(content)
            logger.info("Saved metadata document %s", self.metadata_document)
            logger.info(
                "Metadata content",
                extra={"metadata_content": json.loads(content)},
            )
        else:
            msg = "No metadata document to save"
            raise ValueError(msg)

    @property
    def percent_complete(self) -> int:
        """The percentage of obligatory metadata completed.

        A metadata field is counted as complete when any non-None value is
        assigned. Used for a live progress bar in the UI, as well as being
        saved in the datadoc as a simple quality indicator.
        """
        num_all_fields = NUM_OBLIGATORY_DATASET_FIELDS + (
            NUM_OBLIGATORY_VARIABLES_FIELDS * len(self.variables)
        )
        num_set_fields = num_obligatory_dataset_fields_completed(
            self.dataset,
        ) + num_obligatory_variables_fields_completed(self.variables)
        return calculate_percentage(num_set_fields, num_all_fields)

    def add_pseudonymization(
        self,
        variable_short_name: str,
        pseudonymization: all_optional_model.Pseudonymization | None = None,
    ) -> None:
        """Adds a new pseudo variable to the list of pseudonymized variables.

        If `pseudonymization` is not supplied, an empty Pseudonymization structure
        will be created and assigned to the variable.
        If an encryption algorithm is recognized (one of the standard Dapla algorithms), default values are filled
        for any missing fields.

        Args:
            variable_short_name: The short name for the variable that one wants to update the pseudo for.
            pseudonymization: The updated pseudonymization.

        """
        variable = self.variables_lookup[variable_short_name]
        if pseudonymization:
            set_default_values_pseudonymization(variable, pseudonymization)
        else:
            variable.pseudonymization = all_optional_model.Pseudonymization()

    def remove_pseudonymization(self, variable_short_name: str) -> None:
        """Removes a pseudo variable by using the shortname.

        Updates the pseudo variable lookup by creating a new one.

        Args:
            variable_short_name: The short name for the variable that one wants to remove the pseudo for.
        """
        if self.variables_lookup[variable_short_name].pseudonymization is not None:
            self.variables_lookup[variable_short_name].pseudonymization = None
