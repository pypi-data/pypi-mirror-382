import logging

import datadoc_model.all_optional.model as all_optional_model
import pytest
from pydantic import AnyUrl

from dapla_metadata.datasets.core import Datadoc
from dapla_metadata.datasets.utility.urn import URN_ERROR_MESSAGE_BASE
from dapla_metadata.datasets.utility.urn import SsbNaisDomains
from dapla_metadata.datasets.utility.urn import klass_urn_converter
from dapla_metadata.datasets.utility.urn import vardef_urn_converter

EXAMPLE_KLASS_ID = "91"
EXAMPLE_KLASS_URN = AnyUrl(klass_urn_converter.build_urn(EXAMPLE_KLASS_ID))
EXAMPLE_VARDEF_ID = "hd8sks89"
EXAMPLE_VARDEF_URN = AnyUrl(vardef_urn_converter.build_urn(EXAMPLE_VARDEF_ID))

VARIABLE_DEFINITION_URN_TEST_CASES = [
    *[
        (
            f"https://metadata.{domain.value}/variable-definitions/{EXAMPLE_VARDEF_ID}",
            EXAMPLE_VARDEF_URN,
            False,
        )
        for domain in SsbNaisDomains
    ],
    *[
        (
            f"https://catalog.{domain.value}/variable-definitions/{EXAMPLE_VARDEF_ID}",
            EXAMPLE_VARDEF_URN,
            False,
        )
        for domain in SsbNaisDomains
    ],
    (
        EXAMPLE_VARDEF_URN,
        EXAMPLE_VARDEF_URN,
        False,
    ),
]


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    [
        *VARIABLE_DEFINITION_URN_TEST_CASES,
        ("https://www.vg.no", None, True),
    ],
)
def test_convert_to_vardef_urn(
    case: str,
    expected_result: AnyUrl | None,
    expect_warning: bool,  # noqa: ARG001
):
    assert vardef_urn_converter.convert_to_urn(case) == expected_result


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    [
        *VARIABLE_DEFINITION_URN_TEST_CASES,
        ("https://www.vg.no", AnyUrl("https://www.vg.no/"), True),
        (None, None, False),
    ],
)
def test_convert_to_vardef_urn_end_to_end(
    case: str | None,
    expected_result: str | None,
    expect_warning: bool,
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.ERROR)
    meta = Datadoc()
    meta._set_metadata(  # noqa: SLF001
        all_optional_model.DatadocMetadata(
            dataset=all_optional_model.Dataset(),
            variables=[
                all_optional_model.Variable(
                    short_name="my_variable", definition_uri=case
                )
            ],
        )
    )
    if not expected_result:
        assert meta.variables[0].definition_uri is None
    else:
        assert meta.variables[0].definition_uri == expected_result
    assert (URN_ERROR_MESSAGE_BASE in caplog.text) is expect_warning


CLASSIFICATION_URN_TEST_CASES = [
    (
        f"https://www.ssb.no/klass/klassifikasjoner/{EXAMPLE_KLASS_ID}",
        EXAMPLE_KLASS_URN,
        False,
    ),
    (
        f"https://www.ssb.no/en/klass/klassifikasjoner/{EXAMPLE_KLASS_ID}",
        EXAMPLE_KLASS_URN,
        False,
    ),
    (
        f"https://data.ssb.no/api/klass/v1/classifications/{EXAMPLE_KLASS_ID}",
        EXAMPLE_KLASS_URN,
        False,
    ),
    (
        f"https://data.ssb.no/api/klass/v1/classifications/{EXAMPLE_KLASS_ID}.json",
        EXAMPLE_KLASS_URN,
        False,
    ),
    (
        EXAMPLE_KLASS_URN,
        EXAMPLE_KLASS_URN,
        False,
    ),
]


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    CLASSIFICATION_URN_TEST_CASES,
)
def test_convert_to_klass_urn(
    case: str,
    expected_result: str,
    expect_warning: bool,  # noqa: ARG001
):
    assert klass_urn_converter.convert_to_urn(case) == expected_result


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    [
        *CLASSIFICATION_URN_TEST_CASES,
        ("https://www.vg.no", AnyUrl("https://www.vg.no/"), True),
        (None, None, False),
    ],
)
def test_convert_to_klass_urn_end_to_end(
    case: str | None,
    expected_result: str | None,
    expect_warning: bool,
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.ERROR)
    meta = Datadoc()
    meta._set_metadata(  # noqa: SLF001
        all_optional_model.DatadocMetadata(
            dataset=all_optional_model.Dataset(),
            variables=[
                all_optional_model.Variable(
                    short_name="my_variable", classification_uri=case
                )
            ],
        )
    )
    if not expected_result:
        assert meta.variables[0].classification_uri is None
    else:
        assert meta.variables[0].classification_uri == expected_result
    assert (URN_ERROR_MESSAGE_BASE in caplog.text) is expect_warning
