"""iGEM Registry API.

This package provides a programmatic interface to the iGEM Registry API,
enabling users to interact with the Registry's data and services.
"""

from .account import Account, Roles
from .annotation import Annotation, Form
from .author import Author
from .calls import PaginatedResponse, call, call_paginated
from .category import Category
from .client import Client, HealthStatus
from .license import License
from .organisation import Organisation
from .part import Compatibility, Part, Reference, Standard, Status
from .type import Type
from .utils import dump

__all__: list[str] = [
    "Account",
    "Annotation",
    "Author",
    "Category",
    "Client",
    "Compatibility",
    "Form",
    "HealthStatus",
    "License",
    "Organisation",
    "PaginatedResponse",
    "Part",
    "Reference",
    "Roles",
    "Standard",
    "Status",
    "Type",
    "call",
    "call_paginated",
    "dump",
]
