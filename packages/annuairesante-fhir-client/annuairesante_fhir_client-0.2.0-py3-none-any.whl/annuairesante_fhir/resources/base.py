"""Base resource wrapper."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..exceptions import FHIRError
from ..models import BundleResponse

if TYPE_CHECKING:
    from ..client import AnnuaireSanteClient


class BaseResource:
    """Base class for FHIR resource wrappers.

    Args:
        client: The AnnuaireSanteClient instance
        resource_type: FHIR resource type name
    """

    def __init__(self, client: "AnnuaireSanteClient", resource_type: str):
        self.client = client
        self.resource_type = resource_type
        self.base_path = f"/{resource_type}"

    def _parse_bundle_response(self, response_data: Dict) -> BundleResponse:
        """Parse a FHIR Bundle response.

        Args:
            response_data: Raw response data from API

        Returns:
            BundleResponse containing parsed data

        Raises:
            FHIRError: If parsing fails
        """
        try:
            # Extract basic bundle info without strict FHIR validation
            total = response_data.get("total", 0)

            # Extract entries as raw dictionaries
            entries = []
            if "entry" in response_data:
                for entry_data in response_data["entry"]:
                    if "resource" in entry_data:
                        entries.append(entry_data["resource"])

            # Extract next link for pagination
            next_url = None
            if "link" in response_data:
                for link in response_data["link"]:
                    if link.get("relation") == "next":
                        next_url = link.get("url")
                        break

            return BundleResponse(
                total=total,
                entries=entries,
                next_url=next_url,
            )
        except (KeyError, ValueError, TypeError) as e:
            raise FHIRError(f"Failed to parse FHIR Bundle: {e}")

    def search(self, **kwargs) -> BundleResponse:
        """Search for resources.

        Args:
            **kwargs: Search parameters

        Returns:
            BundleResponse containing search results
        """
        # Remove None values
        params = {k: v for k, v in kwargs.items() if v is not None}

        # Make API request
        response_data = self.client.get(self.base_path, params=params)

        # Parse FHIR Bundle
        return self._parse_bundle_response(response_data)

    def read(self, resource_id: str) -> Any:
        """Read a specific resource by ID.

        Args:
            resource_id: Resource ID

        Returns:
            FHIR resource
        """
        path = f"{self.base_path}/{resource_id}"
        response_data = self.client.get(path)

        try:
            # Dynamically import the resource class
            from fhir.resources import get_fhir_model_class

            resource_class = get_fhir_model_class(self.resource_type)
            return resource_class.parse_obj(response_data)
        except (KeyError, ValueError, TypeError, AttributeError, ImportError) as e:
            raise FHIRError(f"Failed to parse {self.resource_type}: {e}")

    def search_all(self, max_results: Optional[int] = None, **kwargs) -> List[Any]:
        """Search and retrieve all results with automatic pagination.

        Args:
            max_results: Maximum number of results to retrieve (None for all)
            **kwargs: Search parameters

        Returns:
            List of all FHIR resources matching the search

        Note:
            Pagination is done by following 'next' links in Bundle responses.
            The Annuaire Santé API does not support _count/_offset parameters.
        """
        all_entries = []
        result = self.search(**kwargs)
        all_entries.extend(result.entries)

        # Follow 'next' links for pagination
        while result.next_url:
            # Check if we've reached the limit
            if max_results and len(all_entries) >= max_results:
                return all_entries[:max_results]

            # Fetch next page using the next_url
            try:
                response_data = self.client.http_client.get(result.next_url).json()
                result = self._parse_bundle_response(response_data)
                all_entries.extend(result.entries)

            except (KeyError, ValueError, TypeError, FHIRError):
                # If parsing next page fails, stop pagination
                break

        return all_entries[:max_results] if max_results else all_entries
