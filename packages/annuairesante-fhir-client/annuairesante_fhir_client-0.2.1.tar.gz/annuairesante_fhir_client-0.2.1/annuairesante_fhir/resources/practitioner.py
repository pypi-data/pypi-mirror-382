"""Practitioner resource wrapper."""

from typing import List, Optional

from fhir.resources.practitioner import Practitioner

from ..models import BundleResponse, PractitionerSearchParams
from .base import BaseResource


class PractitionerResource(BaseResource):
    """Wrapper for Practitioner FHIR resource."""

    def __init__(self, client):
        super().__init__(client, "Practitioner")

    def search(
        self,
        # Paramètres de base
        family: Optional[str] = None,
        given: Optional[str] = None,
        identifier: Optional[str] = None,
        name: Optional[str] = None,
        telecom: Optional[str] = None,
        # Paramètres standards FHIR
        active: Optional[bool] = None,
        id: Optional[str] = None,
        last_updated: Optional[str] = None,
        # Paramètres spécifiques Annuaire Santé
        data_information_system: Optional[str] = None,
        identifier_type: Optional[str] = None,
        mailbox_mss: Optional[str] = None,
        number_smartcard: Optional[str] = None,
        qualification_code: Optional[str] = None,
        **kwargs,
    ) -> BundleResponse:
        """Search for practitioners.

        Args:
            family: Family name (last name)
            given: Given name (first name)
            identifier: Professional identifier (RPPS, ADELI, etc.)
            name: Full name search
            telecom: Email or phone
            active: Search only active practitioners
            id: Technical resource ID
            last_updated: Last update date
            data_information_system: Information system (RPPS, ADELI, etc.)
            identifier_type: Identifier type
            mailbox_mss: Secure messaging mailbox
            number_smartcard: CPS/CPF card number
            qualification_code: Qualification/diploma code
            **kwargs: Additional search parameters

        Returns:
            BundleResponse containing Practitioner resources

        Note:
            Pagination is handled via 'next' links in the response.
            Use search_all() for automatic pagination.
        """
        params = PractitionerSearchParams(
            family=family,
            given=given,
            identifier=identifier,
            name=name,
            telecom=telecom,
            active=active,
            id=id,
            last_updated=last_updated,
            data_information_system=data_information_system,
            identifier_type=identifier_type,
            mailbox_mss=mailbox_mss,
            number_smartcard=number_smartcard,
            qualification_code=qualification_code,
        )

        return super().search(**params.to_dict(), **kwargs)

    def read(self, resource_id: str) -> Practitioner:
        """Read a specific Practitioner by ID.

        Args:
            resource_id: Practitioner ID

        Returns:
            Practitioner resource
        """
        return super().read(resource_id)

    def search_all(self, max_results: Optional[int] = None, **kwargs) -> List[dict]:
        """Search and retrieve all practitioners with automatic pagination.

        Args:
            max_results: Maximum number of results to retrieve
            **kwargs: Search parameters

        Returns:
            List of Practitioner resources (as dictionaries)

        Note:
            Pagination follows 'next' links in Bundle responses.
        """
        return super().search_all(max_results=max_results, **kwargs)

    def search_by_rpps(self, rpps: str) -> Optional[Practitioner]:
        """Search for a practitioner by RPPS identifier.

        Args:
            rpps: RPPS identifier

        Returns:
            Practitioner resource or None if not found
        """
        result = self.search(identifier=rpps)
        return result.entries[0] if result.entries else None

    def search_by_name(self, family: str, given: Optional[str] = None) -> List[Practitioner]:
        """Search for practitioners by name.

        Args:
            family: Family name (required)
            given: Given name (optional)

        Returns:
            List of matching Practitioner resources
        """
        result = self.search(family=family, given=given)
        return result.entries
