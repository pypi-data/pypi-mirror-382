"""Model Backwards Compatibility.

This package contains code for upgrading existing metadata documents to the newest version of the model.
This is analogous to a Database Migration where the structure of the data has changed and we wish to
retain already persisted information.

"""

from ._utils import is_metadata_in_container_structure
from .model_backwards_compatibility import upgrade_metadata
