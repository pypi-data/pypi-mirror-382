"""Device resource wrapper."""

from typing import List, Optional

from fhir.resources.device import Device

from ..models import BundleResponse, DeviceSearchParams
from .base import BaseResource


class DeviceResource(BaseResource):
    """Wrapper for Device FHIR resource."""

    def __init__(self, client):
        super().__init__(client, "Device")

    def search(
        self,
        # Paramètres de base
        identifier: Optional[str] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
        organization: Optional[str] = None,
        # Paramètres standards FHIR
        id: Optional[str] = None,
        last_updated: Optional[str] = None,
        # Paramètres spécifiques Annuaire Santé
        manufacturer: Optional[str] = None,
        model: Optional[str] = None,
        data_information_system: Optional[str] = None,
        **kwargs,
    ) -> BundleResponse:
        """Search for devices.

        Args:
            identifier: Device identifier
            type: Device type code
            status: Device status (active, inactive, etc.)
            organization: Reference to Organization (e.g., "Organization/123")
            id: Technical resource ID
            last_updated: Last update date
            manufacturer: Device manufacturer/brand
            model: Device model
            data_information_system: Information system
            **kwargs: Additional search parameters

        Returns:
            BundleResponse containing Device resources
        """
        params = DeviceSearchParams(
            identifier=identifier,
            type=type,
            status=status,
            organization=organization,
            id=id,
            last_updated=last_updated,
            manufacturer=manufacturer,
            model=model,
            data_information_system=data_information_system,
        )

        return super().search(**params.to_dict(), **kwargs)

    def read(self, resource_id: str) -> Device:
        """Read a specific Device by ID.

        Args:
            resource_id: Device ID

        Returns:
            Device resource
        """
        return super().read(resource_id)

    def search_all(
        self, max_results: Optional[int] = None, page_size: int = 50, **kwargs
    ) -> List[Device]:
        """Search and retrieve all devices with automatic pagination.

        Args:
            max_results: Maximum number of results to retrieve
            page_size: Number of results per page
            **kwargs: Search parameters

        Returns:
            List of Device resources
        """
        return super().search_all(max_results=max_results, page_size=page_size, **kwargs)
