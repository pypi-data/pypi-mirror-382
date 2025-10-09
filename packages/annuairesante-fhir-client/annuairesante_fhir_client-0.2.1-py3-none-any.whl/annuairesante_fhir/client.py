"""Core client for Annuaire Santé FHIR API."""

import os
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx

from .exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class AnnuaireSanteClient:
    """Client for Annuaire Santé FHIR API.

    Args:
        api_key: API key for authentication. If not provided, will look for
                ANNUAIRE_SANTE_API_KEY environment variable.
        base_url: Base URL for the API. Defaults to production URL.
        timeout: Request timeout in seconds. Defaults to 30.
    """

    DEFAULT_BASE_URL = "https://gateway.api.esante.gouv.fr/fhir/v2"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        # Load environment variables if needed
        if api_key is None and not os.getenv("ANNUAIRE_SANTE_API_KEY"):
            try:
                from dotenv import load_dotenv

                load_dotenv()
            except ImportError:
                pass  # python-dotenv not installed

        self.api_key = api_key or os.getenv("ANNUAIRE_SANTE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Provide it via api_key parameter or "
                "ANNUAIRE_SANTE_API_KEY environment variable."
            )

        self.base_url = base_url or self.DEFAULT_BASE_URL

        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.timeout = timeout

        # Initialize HTTP client
        self.http_client = httpx.Client(
            timeout=timeout,
            headers=self._get_headers(),
        )

        # Lazy-load resource wrappers
        self._practitioner = None
        self._organization = None
        self._practitioner_role = None
        self._healthcare_service = None
        self._device = None

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "ESANTE-API-KEY": self.api_key,
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        }

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        # Ensure base_url ends with / and path doesn't start with /
        base = self.base_url.rstrip("/") + "/"
        path = path.lstrip("/")
        return urljoin(base, path)

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise AuthenticationError("Invalid API key or authentication failed")
        elif response.status_code == 404:
            raise NotFoundError("Resource not found")
        elif response.status_code == 400:
            raise ValidationError(f"Validation error: {response.text}")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif 500 <= response.status_code < 600:
            raise ServerError(f"Server error: {response.status_code} - {response.text}")
        else:
            raise Exception(f"Unexpected error: {response.status_code} - {response.text}")

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make GET request to API.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Parsed JSON response
        """
        url = self._build_url(path)
        response = self.http_client.get(url, params=params)
        return self._handle_response(response)

    def post(self, path: str, data: Dict[str, Any]) -> Any:
        """Make POST request to API.

        Args:
            path: API endpoint path
            data: Request body

        Returns:
            Parsed JSON response
        """
        url = self._build_url(path)
        response = self.http_client.post(url, json=data)
        return self._handle_response(response)

    @property
    def practitioner(self):
        """Get Practitioner resource wrapper."""
        if self._practitioner is None:
            from .resources.practitioner import PractitionerResource

            self._practitioner = PractitionerResource(self)
        return self._practitioner

    @property
    def organization(self):
        """Get Organization resource wrapper."""
        if self._organization is None:
            from .resources.organization import OrganizationResource

            self._organization = OrganizationResource(self)
        return self._organization

    @property
    def practitioner_role(self):
        """Get PractitionerRole resource wrapper."""
        if self._practitioner_role is None:
            from .resources.practitioner_role import PractitionerRoleResource

            self._practitioner_role = PractitionerRoleResource(self)
        return self._practitioner_role

    @property
    def healthcare_service(self):
        """Get HealthcareService resource wrapper."""
        if self._healthcare_service is None:
            from .resources.healthcare_service import HealthcareServiceResource

            self._healthcare_service = HealthcareServiceResource(self)
        return self._healthcare_service

    @property
    def device(self):
        """Get Device resource wrapper."""
        if self._device is None:
            from .resources.device import DeviceResource

            self._device = DeviceResource(self)
        return self._device

    def metadata(self) -> Dict[str, Any]:
        """Get CapabilityStatement (server metadata).

        Returns:
            CapabilityStatement resource
        """
        return self.get("/metadata")

    def close(self):
        """Close HTTP client."""
        self.http_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
