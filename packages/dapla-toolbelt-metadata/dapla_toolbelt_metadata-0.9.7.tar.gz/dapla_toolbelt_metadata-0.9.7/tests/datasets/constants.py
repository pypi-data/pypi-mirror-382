"""Repository for constant values for Datadoc tests."""

from pathlib import Path

from datadoc_model.all_optional.model import DataType

TEST_BUCKET_PARQUET_FILEPATH = "gs://ssb-staging-dapla-felles-data-delt/datadoc/klargjorte_data/person_data_v1.parquet"

TEST_BUCKET_PARQUET_FILEPATH_WITH_SHORTNAME = "gs://ssb-staging-dapla-felles-data-delt/befolkning/klargjorte_data/person_data_v1.parquet"

TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH = "gs://ssb-my-team-data-produkt-prod/ifpn/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet"

TEST_RESOURCES_DIRECTORY = Path("tests/datasets/resources")

TEST_DATASETS_DIRECTORY = TEST_RESOURCES_DIRECTORY / "datasets"

TEST_PARQUET_FILE_NAME = "person_data_v1.parquet"

TEST_NAMING_STANDARD_COMPATIBLE_DATASET = (
    "ifpn/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet"
)

TEST_PARQUET_FILEPATH = TEST_DATASETS_DIRECTORY / TEST_PARQUET_FILE_NAME

TEST_SAS7BDAT_FILEPATH = TEST_DATASETS_DIRECTORY / "sasdata.sas7bdat"

TEST_PARQUET_GZIP_FILEPATH = TEST_DATASETS_DIRECTORY / "person_data_v1.parquet.gzip"

TEST_EXISTING_METADATA_DIRECTORY = TEST_RESOURCES_DIRECTORY / "existing_metadata_file"

TEST_EXISTING_METADATA_FILE_NAME = "person_data_v1__DOC.json"

TEST_EXISTING_METADATA_FILEPATH = (
    TEST_EXISTING_METADATA_DIRECTORY / TEST_EXISTING_METADATA_FILE_NAME
)

TEST_EXISTING_METADATA_NAMING_STANDARD_FILEPATH = (
    TEST_EXISTING_METADATA_DIRECTORY
    / "person_testdata_p2020-12-31_p2020-12-31_v1__DOC.json"
)

TEST_EXISTING_METADATA_WITH_VALID_ID_DIRECTORY = (
    TEST_EXISTING_METADATA_DIRECTORY / "valid_id_field"
)

TEST_COMPATIBILITY_DIRECTORY = TEST_EXISTING_METADATA_DIRECTORY / "compatibility"

TEST_PSEUDO_DIRECTORY = TEST_EXISTING_METADATA_DIRECTORY / "pseudo"

TEST_PROCESSED_DATA_POPULATION_DIRECTORY = TEST_RESOURCES_DIRECTORY / "klargjorte_data"


CODE_LIST_DIR = "code_list"

DATADOC_METADATA_MODULE = "dapla_metadata.datasets"

DATADOC_METADATA_MODULE_CORE = "dapla_metadata.datasets.core"

DATADOC_METADATA_MODULE_UTILS = "dapla_metadata.datasets.utility.utils"

VARIABLE_SHORT_NAMES = [
    "fnr",
    "sivilstand",
    "bostedskommune",
    "inntekt",
    "bankinnskudd",
    "dato",
]


VARIABLE_DATA_TYPES = [
    DataType.STRING,
    DataType.STRING,
    DataType.STRING,
    DataType.INTEGER,
    DataType.INTEGER,
    DataType.DATETIME,
]
