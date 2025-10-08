"""Tests for AnnuaireSanteClient."""

import pytest
from unittest.mock import Mock, patch

from annuairesante_fhir import AnnuaireSanteClient
from annuairesante_fhir.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)


def test_client_initialization_with_api_key():
    """Test client initialization with API key."""
    client = AnnuaireSanteClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.base_url == AnnuaireSanteClient.DEFAULT_BASE_URL
    client.close()


def test_client_initialization_without_api_key():
    """Test client initialization without API key raises error."""
    with patch.dict("os.environ", {}, clear=True):
        # Mock python-dotenv import to prevent it from loading .env
        with patch("builtins.__import__", side_effect=ImportError):
            with pytest.raises(AuthenticationError):
                AnnuaireSanteClient()


def test_client_context_manager():
    """Test client can be used as context manager."""
    with AnnuaireSanteClient(api_key="test_key") as client:
        assert client.api_key == "test_key"


@patch("annuairesante_fhir.client.httpx.Client")
def test_client_get_request(mock_httpx):
    """Test GET request handling."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"resourceType": "Bundle"}

    mock_httpx.return_value.get.return_value = mock_response

    client = AnnuaireSanteClient(api_key="test_key")
    result = client.get("/Practitioner")

    assert result == {"resourceType": "Bundle"}
    client.close()


@patch("annuairesante_fhir.client.httpx.Client")
def test_client_handles_404(mock_httpx):
    """Test 404 response raises NotFoundError."""
    mock_response = Mock()
    mock_response.status_code = 404

    mock_httpx.return_value.get.return_value = mock_response

    client = AnnuaireSanteClient(api_key="test_key")

    with pytest.raises(NotFoundError):
        client.get("/Practitioner/invalid-id")

    client.close()


@patch("annuairesante_fhir.client.httpx.Client")
def test_client_handles_401(mock_httpx):
    """Test 401 response raises AuthenticationError."""
    mock_response = Mock()
    mock_response.status_code = 401

    mock_httpx.return_value.get.return_value = mock_response

    client = AnnuaireSanteClient(api_key="invalid_key")

    with pytest.raises(AuthenticationError):
        client.get("/Practitioner")

    client.close()


@patch("annuairesante_fhir.client.httpx.Client")
def test_client_handles_429(mock_httpx):
    """Test 429 response raises RateLimitError."""
    mock_response = Mock()
    mock_response.status_code = 429

    mock_httpx.return_value.get.return_value = mock_response

    client = AnnuaireSanteClient(api_key="test_key")

    with pytest.raises(RateLimitError):
        client.get("/Practitioner")

    client.close()


def test_client_headers():
    """Test client sets correct headers."""
    client = AnnuaireSanteClient(api_key="test_key")
    headers = client._get_headers()

    assert headers["ESANTE-API-KEY"] == "test_key"
    assert headers["Accept"] == "application/fhir+json"
    assert headers["Content-Type"] == "application/fhir+json"

    client.close()
