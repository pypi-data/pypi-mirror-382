"""Mithril API interaction layer.

This package handles communication with the Mithril API:
- API data types and models
- Error handling and response validation

Modules under this package should only contain HTTP request wrappers and
data transfer objects for provider-specific payloads. Business logic belongs
in `domain/` services.
"""

from flow.adapters.providers.builtin.mithril.api.handlers import (
    handle_mithril_errors,
    validate_response,
)
from flow.adapters.providers.builtin.mithril.api.types import (
    AuctionModel,
    GPUModel,
    InstanceTypeModel,
    InstanceTypesResponse,
    ProjectModel,
    SpotAvailabilityResponse,
    SSHKeyModel,
)

__all__ = [
    "AuctionModel",
    "GPUModel",
    "InstanceTypeModel",
    "InstanceTypesResponse",
    # Types
    "ProjectModel",
    "SSHKeyModel",
    "SpotAvailabilityResponse",
    # Handlers
    "handle_mithril_errors",
    "validate_response",
]
