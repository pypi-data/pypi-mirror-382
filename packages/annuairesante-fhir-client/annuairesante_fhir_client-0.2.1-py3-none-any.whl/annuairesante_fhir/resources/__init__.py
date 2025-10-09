"""Resource wrappers for FHIR resources."""

from .base import BaseResource
from .device import DeviceResource
from .healthcare_service import HealthcareServiceResource
from .organization import OrganizationResource
from .practitioner import PractitionerResource
from .practitioner_role import PractitionerRoleResource

__all__ = [
    "BaseResource",
    "PractitionerResource",
    "OrganizationResource",
    "PractitionerRoleResource",
    "HealthcareServiceResource",
    "DeviceResource",
]
