import pytest
from klass import KlassClassification

from dapla_metadata.datasets.code_list import CodeList
from dapla_metadata.datasets.utility.enums import SupportedLanguages
from tests.datasets.constants import TEST_RESOURCES_DIRECTORY

CODE_LIST_DIR = "code_list"


@pytest.mark.parametrize(
    (
        "code_list_csv_filepath_nb",
        "code_list_csv_filepath_nn",
        "code_list_csv_filepath_en",
        "titles",
        "codes",
    ),
    [
        (
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nb.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nn.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_en.csv",
            ["Adresse", "Arbeidsulykke", "Bolig"],
            ["01", "02", "03"],
        ),
        (
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "no_code.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "no_code.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "no_code.csv",
            ["Adresse", "Arbeidsulykke", "Bolig"],
            [None, None, None],
        ),
    ],
)
@pytest.mark.usefixtures("_mock_fetch_dataframe")
def test_read_dataframe(
    code_list_fake_structure: CodeList,
    codes: list[str],
    titles: list[str],
):
    code_list_fake_structure.wait_for_external_result()

    for i in range(3):
        assert code_list_fake_structure.classifications[i].code == codes[i]

    for idx in range(3):
        classification = code_list_fake_structure.classifications[idx]
        assert classification.get_title(SupportedLanguages.NORSK_BOKMÅL) == titles[idx]
        assert classification.get_title(SupportedLanguages.ENGLISH) == titles[idx]
        assert classification.get_title(SupportedLanguages.NORSK_NYNORSK) == titles[idx]


def test_non_existent_code(thread_pool_executor):
    code_list = CodeList(thread_pool_executor, 0)
    code_list.wait_for_external_result()
    assert code_list.classifications == []


@pytest.mark.parametrize("language", list(SupportedLanguages))
def test_instantiate_classification(language: SupportedLanguages):
    # This started failing when casting the enum language argument
    # to a str, so we write a test to cover this eventuality.
    assert isinstance(
        KlassClassification("6", language.lower()),  # type: ignore [arg-type]
        KlassClassification,
    )
