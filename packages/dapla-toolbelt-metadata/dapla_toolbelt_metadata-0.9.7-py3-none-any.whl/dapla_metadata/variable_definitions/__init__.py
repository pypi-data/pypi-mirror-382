"""Client for working with Variable Definitions at Statistics Norway."""

from ._generated.vardef_client import models
from ._generated.vardef_client.exceptions import *  # noqa: F403
from ._utils.constants import DEFAULT_DATE
from ._utils.constants import GENERATED_CONTACT
from .exceptions import VardefClientError
from .exceptions import VardefFileError
from .exceptions import VariableNotFoundError
from .vardef import Vardef
from .variable_definition import VariableDefinition
