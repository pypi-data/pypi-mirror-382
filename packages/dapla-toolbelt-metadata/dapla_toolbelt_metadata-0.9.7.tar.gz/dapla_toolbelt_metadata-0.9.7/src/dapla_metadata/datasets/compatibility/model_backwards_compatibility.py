"""Upgrade old metadata files to be compatible with new versions.

An important principle of Datadoc is that we ALWAYS guarantee backwards
compatibility of existing metadata documents. This means that we guarantee
that a user will never lose data, even if their document is decades old.

For each document version we release with breaking changes, we implement a
handler and register the version by defining a BackwardsCompatibleVersion
instance. These documents will then be upgraded when they're opened in Datadoc.

A test must also be implemented for each new version.
"""

from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from dapla_metadata.datasets.compatibility._handlers import handle_current_version
from dapla_metadata.datasets.compatibility._handlers import handle_version_0_1_1
from dapla_metadata.datasets.compatibility._handlers import handle_version_1_0_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_2_1_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_2_2_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_3_1_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_3_2_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_3_3_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_4_0_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_5_0_1
from dapla_metadata.datasets.compatibility._handlers import handle_version_6_0_0
from dapla_metadata.datasets.compatibility._utils import DATADOC_KEY
from dapla_metadata.datasets.compatibility._utils import DOCUMENT_VERSION_KEY
from dapla_metadata.datasets.compatibility._utils import UnknownModelVersionError
from dapla_metadata.datasets.compatibility._utils import (
    is_metadata_in_container_structure,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Callable

SUPPORTED_VERSIONS: OrderedDict[str, BackwardsCompatibleVersion] = OrderedDict()


@dataclass()
class BackwardsCompatibleVersion:
    """A version which we support with backwards compatibility.

    This class registers a version and its corresponding handler function
    for backwards compatibility.
    """

    version: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]

    def __post_init__(self) -> None:
        """Register this version in the supported versions map.

        This method adds the instance to the `SUPPORTED_VERSIONS` dictionary
        using the version as the key.
        """
        SUPPORTED_VERSIONS[self.version] = self

    def upgrade(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Upgrade metadata from the format of the previous version to the format of this version.

        This method handles bumping the Document Version field so it's not necessary to do this in
        the individual handler functions.

        Args:
            metadata (dict[str, Any]): Metadata in the format of the previous version, to be upgraded.

        Returns:
            dict[str, Any]: The metadata upgraded to the version specified
        """
        metadata = self.handler(metadata)
        if is_metadata_in_container_structure(metadata):
            metadata[DATADOC_KEY][DOCUMENT_VERSION_KEY] = self.version
        else:
            metadata[DOCUMENT_VERSION_KEY] = self.version
        return metadata


# Register all the supported versions and their handlers.
BackwardsCompatibleVersion(version="0.1.1", handler=handle_version_0_1_1)
BackwardsCompatibleVersion(version="1.0.0", handler=handle_version_1_0_0)
BackwardsCompatibleVersion(version="2.1.0", handler=handle_version_2_1_0)
BackwardsCompatibleVersion(version="2.2.0", handler=handle_version_2_2_0)
BackwardsCompatibleVersion(version="3.1.0", handler=handle_version_3_1_0)
BackwardsCompatibleVersion(version="3.2.0", handler=handle_version_3_2_0)
BackwardsCompatibleVersion(version="3.3.0", handler=handle_version_3_3_0)
BackwardsCompatibleVersion(version="4.0.0", handler=handle_version_4_0_0)
BackwardsCompatibleVersion(version="5.0.1", handler=handle_version_5_0_1)
BackwardsCompatibleVersion(version="6.0.0", handler=handle_version_6_0_0)
BackwardsCompatibleVersion(version="6.1.0", handler=handle_current_version)


def upgrade_metadata(fresh_metadata: dict[str, Any]) -> dict[str, Any]:
    """Upgrade the metadata to the latest version using registered handlers.

    This function checks the version of the provided metadata and applies a series
    of upgrade handlers to migrate the metadata to the latest version.
    It starts from the provided version and applies all subsequent handlers in
    sequence. If the metadata is already in the latest version or the version
    cannot be determined, appropriate actions are taken.

    Args:
        fresh_metadata: The metadata dictionary to be upgraded. This dictionary
            must include version information that determines which handlers to apply.

    Returns:
        The upgraded metadata dictionary, after applying all necessary handlers.

    Raises:
        UnknownModelVersionError: If the metadata's version is unknown or unsupported.
    """
    if is_metadata_in_container_structure(fresh_metadata):
        if fresh_metadata[DATADOC_KEY] is None:
            return fresh_metadata
        supplied_version = fresh_metadata[DATADOC_KEY][DOCUMENT_VERSION_KEY]
    else:
        supplied_version = fresh_metadata[DOCUMENT_VERSION_KEY]
    start_running_handlers = False
    # Run all the handlers in order from the supplied version onwards
    for k, v in SUPPORTED_VERSIONS.items():
        if k == supplied_version:
            start_running_handlers = True
        if start_running_handlers:
            fresh_metadata = v.upgrade(fresh_metadata)
    if not start_running_handlers:
        raise UnknownModelVersionError(supplied_version)
    return fresh_metadata
