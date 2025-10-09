"""Annuaire Santé FHIR Client.

A Python client for the French Annuaire Santé FHIR API.
"""

__version__ = "0.2.1"

from .client import AnnuaireSanteClient
from .exceptions import (
    AnnuaireSanteError,
    AuthenticationError,
    FHIRError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .models import (
    BundleResponse,
    DeviceSearchParams,
    HealthcareServiceSearchParams,
    OrganizationSearchParams,
    PractitionerRoleSearchParams,
    PractitionerSearchParams,
    SearchParams,
)

from .helpers import (
    DeviceHelper,
    HealthcareServiceHelper,
    OrganizationHelper,
    PractitionerHelper,
    PractitionerRoleHelper,
    wrap_device,
    wrap_healthcare_service,
    wrap_organization,
    wrap_practitioner,
    wrap_practitioner_role,
)

__all__ = [
    "AnnuaireSanteClient",
    # Exceptions
    "AnnuaireSanteError",
    "AuthenticationError",
    "FHIRError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
    # Models
    "BundleResponse",
    "SearchParams",
    "PractitionerSearchParams",
    "OrganizationSearchParams",
    "PractitionerRoleSearchParams",
    "HealthcareServiceSearchParams",
    "DeviceSearchParams",
    # Helpers
    "PractitionerHelper",
    "OrganizationHelper",
    "PractitionerRoleHelper",
    "HealthcareServiceHelper",
    "DeviceHelper",
    "wrap_practitioner",
    "wrap_organization",
    "wrap_practitioner_role",
    "wrap_healthcare_service",
    "wrap_device",
]
