import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def set_temp_bucket(tmp_path: Path):
    """Fixture which set buckets."""
    buckets_dir = tmp_path / "buckets"
    buckets_dir.mkdir(parents=True, exist_ok=True)
    return buckets_dir


@pytest.fixture
def set_temp_bucket_name(set_temp_bucket):
    """Fixture which set buckets."""
    buckets_name_folder = set_temp_bucket / "bucket_name"
    buckets_name_folder.mkdir(parents=True, exist_ok=True)
    return buckets_name_folder


@pytest.fixture(scope="module")
def test_directory():
    """Creates a temporary directory with test files and subdirectories."""
    temp_dir = Path(tempfile.mkdtemp())  # Create temp directory

    # Create valid and invalid files
    (
        temp_dir
        / "ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet"
    ).touch()
    (
        temp_dir / "stat/inndata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet"
    ).touch()
    (
        temp_dir
        / "ssb-dapla-example-data-produkt-prod/ledstill/inndata/skjema_p2018_p2020_v1"
    ).touch()
    (
        temp_dir
        / "tests/dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet"
    ).touch()

    # Create a subdirectory with more files
    sub_dir = temp_dir / "subdir"
    sub_dir.mkdir()
    (
        sub_dir / "produkt/test-2/person_testdata_p2021-12-31_p2021-12-31_v1.parquet"
    ).touch()

    yield temp_dir  # Provide temp directory path to tests

    shutil.rmtree(temp_dir)  # Cleanup after tests
