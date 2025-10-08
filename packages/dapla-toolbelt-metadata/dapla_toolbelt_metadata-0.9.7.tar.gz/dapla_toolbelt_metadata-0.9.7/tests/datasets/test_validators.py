"""Tests for validators for DatadocMetadata class."""

from __future__ import annotations

import datetime
import re
import warnings
from typing import TYPE_CHECKING

import pytest
from datadoc_model import model
from pydantic import ValidationError

from dapla_metadata.datasets.model_validation import ObligatoryDatasetWarning
from dapla_metadata.datasets.model_validation import ObligatoryVariableWarning
from dapla_metadata.datasets.utility.constants import OBLIGATORY_METADATA_WARNING

if TYPE_CHECKING:
    from dapla_metadata.datasets.core import Datadoc


@pytest.mark.parametrize(
    ("model_type", "date_from", "date_until", "raises_exception"),
    [
        ("dataset", datetime.date(2024, 1, 1), datetime.date(1980, 10, 1), True),
        ("dataset", datetime.date(1967, 1, 1), datetime.date(1980, 1, 1), False),
        ("variable", datetime.date(1999, 10, 5), datetime.date(1925, 3, 12), True),
        ("variable", datetime.date(2022, 7, 24), datetime.date(2023, 2, 19), False),
        ("dataset", datetime.date(1967, 1, 1), None, False),
        ("variable", datetime.date(1999, 2, 2), datetime.date(1999, 2, 2), False),
    ],
)
def test_write_metadata_document_validate_date_order(
    model_type,
    date_from,
    date_until,
    raises_exception,
    metadata: Datadoc,
):
    if model_type == "dataset":
        metadata.dataset.contains_data_from = date_from
        metadata.dataset.contains_data_until = date_until
    if model_type == "variable":
        for v in metadata.variables:
            v.contains_data_from = date_from
            v.contains_data_until = date_until
    if raises_exception:
        with pytest.raises(
            ValueError,
            match="contains_data_from must be the same or earlier date than contains_data_until",
        ):
            metadata.write_metadata_document()
    else:
        try:
            metadata.write_metadata_document()
        except ValidationError as exc:
            pytest.fail(str(exc))


def test_write_metadata_document_created_date(
    metadata: Datadoc,
):
    metadata.dataset.metadata_created_date = None
    metadata.write_metadata_document()
    assert metadata.dataset.metadata_created_date is not None


@pytest.mark.parametrize(
    ("variable_date", "date_from", "date_until"),
    [
        (None, datetime.date(1967, 1, 1), datetime.date(1980, 1, 1)),
        (
            datetime.date(2022, 2, 2),
            datetime.date(1999, 3, 3),
            datetime.date(2000, 1, 4),
        ),
    ],
)
def test_variables_inherit_dates(
    variable_date,
    date_from,
    date_until,
    metadata: Datadoc,
):
    metadata.dataset.contains_data_from = date_from
    metadata.dataset.contains_data_until = date_until
    for v in metadata.variables:
        v.contains_data_from = variable_date
        v.contains_data_until = variable_date
    metadata.write_metadata_document()
    for v in metadata.variables:
        if variable_date is None:
            assert v.contains_data_from == metadata.dataset.contains_data_from
            assert v.contains_data_until == metadata.dataset.contains_data_until
        else:
            assert v.contains_data_from == variable_date
            assert v.contains_data_until == variable_date


def test_obligatory_metadata_dataset_warning(metadata: Datadoc):
    with pytest.warns(
        ObligatoryDatasetWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record:
        metadata.write_metadata_document()
    all_obligatory_completed = 100
    num_warnings = 2
    if metadata.percent_complete != all_obligatory_completed:
        assert len(record) == num_warnings
        assert issubclass(record[0].category, ObligatoryDatasetWarning)
        assert OBLIGATORY_METADATA_WARNING in str(
            record[0].message,
        )


def test_obligatory_metadata_variables_warning(metadata: Datadoc):
    with pytest.warns(
        ObligatoryVariableWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record:
        metadata.write_metadata_document()
    all_obligatory_completed = 100
    if metadata.percent_complete != all_obligatory_completed and len(record) > 1:
        assert issubclass(record[1].category, ObligatoryVariableWarning)
        if (
            metadata.variables_lookup["pers_id"]
            and metadata.variables_lookup["pers_id"].name is None
        ):
            assert "[{'pers_id': ['name'," in str(
                record[1].message,
            )


def test_obligatory_metadata_dataset_warning_name(metadata: Datadoc):
    metadata.dataset.name = None
    with pytest.warns(
        ObligatoryDatasetWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record:
        metadata.write_metadata_document()
    assert "name" in str(
        record[0].message,
    )
    # Set value 'name' for first time, a Language object is created
    metadata.dataset.name = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText="Navnet"),
        ],
    )
    metadata.dataset.description = None
    with pytest.warns(
        ObligatoryDatasetWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record2:
        metadata.write_metadata_document()
    assert "name" not in str(record2[0].message)

    # Remove value for 'name', value for 'name' is no longer 'None', but 'languageText' is None
    metadata.dataset.name = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText=""),
        ],
    )
    with pytest.warns(
        ObligatoryDatasetWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record3:
        metadata.write_metadata_document()
    assert "name" in str(record3[0].message)


def test_obligatory_metadata_dataset_warning_description(metadata: Datadoc):
    """Field name 'description' is a special case because it can match other field names like 'version_description'."""
    error_message: str
    missing_obligatory_dataset = ""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryDatasetWarning):
            error_message = str(w[0].message)
    assert re.search(r"\bdescription\b", error_message)

    # Check that field name is removed from warning when value
    metadata.dataset.description = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText="Beskrivelse"),
        ],
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryDatasetWarning):
            missing_obligatory_dataset = str(w[0].message)
    assert not re.search(r"\bdescription\b", missing_obligatory_dataset)


def test_obligatory_metadata_dataset_warning_multiple_languages(
    metadata: Datadoc,
):
    missing_obligatory_dataset = ""

    metadata.dataset.description = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText="Beskrivelse"),
            model.LanguageStringTypeItem(languageCode="en", languageText="Description"),
        ],
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryDatasetWarning):
            missing_obligatory_dataset = str(w[0].message)
    assert not re.search(r"\bdescription\b", missing_obligatory_dataset)

    # Remove value for one language
    metadata.dataset.description = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText=""),
            model.LanguageStringTypeItem(languageCode="en", languageText="Description"),
        ],
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryDatasetWarning):
            missing_obligatory_dataset = str(w[0].message)
    assert not re.search(r"\bdescription\b", missing_obligatory_dataset)

    # Remove value for all languages
    metadata.dataset.description = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText=""),
            model.LanguageStringTypeItem(languageCode="en", languageText=""),
        ],
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryDatasetWarning):
            missing_obligatory_dataset = str(w[0].message)
    assert re.search(r"\bdescription\b", missing_obligatory_dataset)


def test_obligatory_metadata_variables_warning_name(metadata: Datadoc):
    variable_with_name = "{'pers_id': ['name'"
    with pytest.warns(
        ObligatoryVariableWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record:
        metadata.write_metadata_document()
    assert metadata.variables_lookup["pers_id"] is not None
    assert metadata.variables_lookup["pers_id"].name is None
    assert variable_with_name in str(record[1].message)

    metadata.variables_lookup["pers_id"].name = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText="Navnet"),
        ],
    )
    with pytest.warns(
        ObligatoryVariableWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record2:
        metadata.write_metadata_document()
    assert variable_with_name not in str(record2[1].message)


def test_obligatory_metadata_variables_warning_pseudonymization(metadata: Datadoc):
    metadata.variables_lookup["pers_id"].pseudonymization = model.Pseudonymization(
        pseudonymization_time="2022-10-07T07:35:01Z",
        stable_identifier_type="",
        stable_identifier_version="",
        encryption_algorithm=None,
        encryption_algorithm_parameters=[],
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        metadata.write_metadata_document()
        if issubclass(w[1].category, ObligatoryVariableWarning):
            missing_obligatory_dataset = str(w[1].message)
    assert "encryption_algorithm" in str(missing_obligatory_dataset)
