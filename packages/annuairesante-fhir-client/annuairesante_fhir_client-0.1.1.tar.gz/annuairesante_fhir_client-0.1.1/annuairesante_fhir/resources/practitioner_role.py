"""PractitionerRole resource wrapper."""

from typing import List, Optional

from fhir.resources.practitionerrole import PractitionerRole

from ..models import BundleResponse, PractitionerRoleSearchParams
from .base import BaseResource


class PractitionerRoleResource(BaseResource):
    """Wrapper for PractitionerRole FHIR resource."""

    def __init__(self, client):
        super().__init__(client, "PractitionerRole")

    def search(
        self,
        # Paramètres de base
        practitioner: Optional[str] = None,
        organization: Optional[str] = None,
        role: Optional[str] = None,
        specialty: Optional[str] = None,
        active: Optional[bool] = None,
        # Paramètres standards FHIR
        id: Optional[str] = None,
        last_updated: Optional[str] = None,
        # Paramètres spécifiques Annuaire Santé
        identifier: Optional[str] = None,
        data_information_system: Optional[str] = None,
        data_registration_authority: Optional[str] = None,
        mailbox_mss: Optional[str] = None,
        **kwargs,
    ) -> BundleResponse:
        """Search for practitioner roles.

        Args:
            practitioner: Reference to Practitioner (e.g., "Practitioner/123")
            organization: Reference to Organization (e.g., "Organization/456")
            role: Role code
            specialty: Specialty code
            active: Active status
            id: Technical resource ID
            last_updated: Last update date
            identifier: Professional identifier
            data_information_system: Information system
            data_registration_authority: Registration authority
            mailbox_mss: MSS mailbox of the structure
            **kwargs: Additional search parameters

        Returns:
            BundleResponse containing PractitionerRole resources
        """
        params = PractitionerRoleSearchParams(
            practitioner=practitioner,
            organization=organization,
            role=role,
            specialty=specialty,
            active=active,
            id=id,
            last_updated=last_updated,
            identifier=identifier,
            data_information_system=data_information_system,
            data_registration_authority=data_registration_authority,
            mailbox_mss=mailbox_mss,
        )

        return super().search(**params.to_dict(), **kwargs)

    def read(self, resource_id: str) -> PractitionerRole:
        """Read a specific PractitionerRole by ID.

        Args:
            resource_id: PractitionerRole ID

        Returns:
            PractitionerRole resource
        """
        return super().read(resource_id)

    def search_all(
        self, max_results: Optional[int] = None, page_size: int = 50, **kwargs
    ) -> List[PractitionerRole]:
        """Search and retrieve all practitioner roles with automatic pagination.

        Args:
            max_results: Maximum number of results to retrieve
            page_size: Number of results per page
            **kwargs: Search parameters

        Returns:
            List of PractitionerRole resources
        """
        return super().search_all(max_results=max_results, page_size=page_size, **kwargs)
