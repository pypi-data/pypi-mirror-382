"""Organization resource wrapper."""

from typing import List, Optional

from fhir.resources.organization import Organization

from ..models import BundleResponse, OrganizationSearchParams
from .base import BaseResource


class OrganizationResource(BaseResource):
    """Wrapper for Organization FHIR resource."""

    def __init__(self, client):
        super().__init__(client, "Organization")

    def search(
        self,
        # Paramètres de base
        name: Optional[str] = None,
        identifier: Optional[str] = None,
        type: Optional[str] = None,
        address: Optional[str] = None,
        address_city: Optional[str] = None,
        address_postalcode: Optional[str] = None,
        # Paramètres standards FHIR
        active: Optional[bool] = None,
        id: Optional[str] = None,
        last_updated: Optional[str] = None,
        # Paramètres spécifiques Annuaire Santé
        data_information_system: Optional[str] = None,
        identifier_type: Optional[str] = None,
        mailbox_mss: Optional[str] = None,
        partof: Optional[str] = None,
        pharmacy_licence: Optional[str] = None,
        **kwargs,
    ) -> BundleResponse:
        """Search for organizations.

        Args:
            name: Organization name
            identifier: Organization identifier (FINESS, SIRET, etc.)
            type: Organization type code
            address: Full address search
            address_city: City name
            address_postalcode: Postal code
            active: Search only active organizations
            id: Technical resource ID
            last_updated: Last update date
            data_information_system: Information system
            identifier_type: Identifier type
            mailbox_mss: Secure messaging mailboxes
            partof: Geographic establishments of a legal entity
            pharmacy_licence: Pharmacy license number
            **kwargs: Additional search parameters

        Returns:
            BundleResponse containing Organization resources
        """
        params = OrganizationSearchParams(
            name=name,
            identifier=identifier,
            type=type,
            address=address,
            address_city=address_city,
            address_postalcode=address_postalcode,
            active=active,
            id=id,
            last_updated=last_updated,
            data_information_system=data_information_system,
            identifier_type=identifier_type,
            mailbox_mss=mailbox_mss,
            partof=partof,
            pharmacy_licence=pharmacy_licence,
        )

        return super().search(**params.to_dict(), **kwargs)

    def read(self, resource_id: str) -> Organization:
        """Read a specific Organization by ID.

        Args:
            resource_id: Organization ID

        Returns:
            Organization resource
        """
        return super().read(resource_id)

    def search_all(self, max_results: Optional[int] = None, **kwargs) -> List[dict]:
        """Search and retrieve all organizations with automatic pagination.

        Args:
            max_results: Maximum number of results to retrieve
            **kwargs: Search parameters

        Returns:
            List of Organization resources (as dictionaries)
        """
        return super().search_all(max_results=max_results, **kwargs)

    def search_by_finess(self, finess: str) -> Optional[Organization]:
        """Search for an organization by FINESS identifier.

        Args:
            finess: FINESS identifier

        Returns:
            Organization resource or None if not found
        """
        result = self.search(identifier=finess)
        return result.entries[0] if result.entries else None

    def search_by_city(self, city: str) -> List[Organization]:
        """Search for organizations by city.

        Args:
            city: City name

        Returns:
            List of matching Organization resources
        """
        result = self.search(address_city=city)
        return result.entries
