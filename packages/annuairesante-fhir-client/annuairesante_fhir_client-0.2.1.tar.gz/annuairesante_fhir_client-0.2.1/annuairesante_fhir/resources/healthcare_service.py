"""HealthcareService resource wrapper."""

from typing import List, Optional

from fhir.resources.healthcareservice import HealthcareService

from ..models import BundleResponse, HealthcareServiceSearchParams
from .base import BaseResource


class HealthcareServiceResource(BaseResource):
    """Wrapper for HealthcareService FHIR resource."""

    def __init__(self, client):
        super().__init__(client, "HealthcareService")

    def search(
        self,
        # Paramètres de base
        name: Optional[str] = None,
        organization: Optional[str] = None,
        service_type: Optional[str] = None,
        active: Optional[bool] = None,
        # Paramètres standards FHIR
        id: Optional[str] = None,
        last_updated: Optional[str] = None,
        profile: Optional[str] = None,
        # Paramètres spécifiques Annuaire Santé
        identifier: Optional[str] = None,
        characteristic: Optional[str] = None,
        service_category: Optional[str] = None,
        **kwargs,
    ) -> BundleResponse:
        """Search for healthcare services.

        Args:
            name: Service name
            organization: Reference to Organization (e.g., "Organization/123")
            service_type: Service type code
            active: Active status
            id: Technical resource ID
            last_updated: Last update date
            profile: Specific profile
            identifier: Specific identifier
            characteristic: Form of activity
            service_category: Healthcare service modality
            **kwargs: Additional search parameters

        Returns:
            BundleResponse containing HealthcareService resources
        """
        params = HealthcareServiceSearchParams(
            name=name,
            organization=organization,
            service_type=service_type,
            active=active,
            id=id,
            last_updated=last_updated,
            profile=profile,
            identifier=identifier,
            characteristic=characteristic,
            service_category=service_category,
        )

        return super().search(**params.to_dict(), **kwargs)

    def read(self, resource_id: str) -> HealthcareService:
        """Read a specific HealthcareService by ID.

        Args:
            resource_id: HealthcareService ID

        Returns:
            HealthcareService resource
        """
        return super().read(resource_id)

    def search_all(
        self, max_results: Optional[int] = None, page_size: int = 50, **kwargs
    ) -> List[HealthcareService]:
        """Search and retrieve all healthcare services with automatic pagination.

        Args:
            max_results: Maximum number of results to retrieve
            page_size: Number of results per page
            **kwargs: Search parameters

        Returns:
            List of HealthcareService resources
        """
        return super().search_all(max_results=max_results, page_size=page_size, **kwargs)
