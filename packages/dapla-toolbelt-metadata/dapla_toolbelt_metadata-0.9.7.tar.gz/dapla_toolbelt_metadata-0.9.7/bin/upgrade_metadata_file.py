"""Script to upgrade metadata documents to the newest version."""

import argparse
from pathlib import Path

from dapla_metadata.datasets.core import Datadoc

parser = argparse.ArgumentParser(
    description="Upgrade metadata documents to the newest version"
)
parser.add_argument(
    "--path",
    nargs="+",
    type=lambda p: Path(p).absolute(),
    help="Path to a metadata document to upgrade",
)
args = parser.parse_args()

for doc in args.path:
    meta = Datadoc(metadata_document_path=str(doc))
    meta.write_metadata_document()
    print(f"Upgraded {doc.stem} to v{meta.container.datadoc.document_version}")  # noqa: T201
