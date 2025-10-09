"""Tests pour les modèles Pydantic."""

import pytest

from annuairesante_fhir.models import (
    DeviceSearchParams,
    HealthcareServiceSearchParams,
    OrganizationSearchParams,
    PractitionerRoleSearchParams,
    PractitionerSearchParams,
)


def test_practitioner_search_params():
    """Test création et sérialisation des paramètres Practitioner."""
    params = PractitionerSearchParams(
        family="Dupont",
        given="Jean",
        identifier="12345678",
    )

    result = params.to_dict()

    assert result["family"] == "Dupont"
    assert result["given"] == "Jean"
    assert result["identifier"] == "12345678"
    assert "active" not in result  # None values excluded


def test_practitioner_search_params_with_alias():
    """Test que les alias sont correctement appliqués."""
    params = PractitionerSearchParams(
        id="123",
        last_updated="ge2025-01-01",
    )

    result = params.to_dict()

    assert result["_id"] == "123"  # Alias appliqué
    assert result["_lastUpdated"] == "ge2025-01-01"  # Alias appliqué


def test_organization_search_params():
    """Test paramètres Organization."""
    params = OrganizationSearchParams(
        name="Hôpital",
        address_postalcode="75",
        identifier="123456789",  # identifier, pas finess directement
    )

    result = params.to_dict()

    assert result["name"] == "Hôpital"
    assert result["address-postalcode"] == "75"  # Alias
    assert result["identifier"] == "123456789"


def test_practitioner_role_search_params():
    """Test paramètres PractitionerRole."""
    params = PractitionerRoleSearchParams(
        practitioner="Practitioner/123",
        organization="Organization/456",
        specialty="SM26",
    )

    result = params.to_dict()

    assert result["practitioner"] == "Practitioner/123"
    assert result["organization"] == "Organization/456"
    assert result["specialty"] == "SM26"


def test_healthcare_service_search_params():
    """Test paramètres HealthcareService."""
    params = HealthcareServiceSearchParams(
        organization="Organization/123",
        service_type="50",
        active=True,
    )

    result = params.to_dict()

    assert result["organization"] == "Organization/123"
    assert result["service-type"] == "50"  # Alias
    assert result["active"] is True


def test_device_search_params():
    """Test paramètres Device."""
    params = DeviceSearchParams(
        identifier="ABC123",
        type="05701",
        manufacturer="SIEMENS",
    )

    result = params.to_dict()

    assert result["identifier"] == "ABC123"
    assert result["type"] == "05701"
    assert result["manufacturer"] == "SIEMENS"


def test_none_values_excluded():
    """Test que les valeurs None ne sont pas incluses."""
    params = PractitionerSearchParams(
        family="Dupont",
        given=None,
        identifier=None,
    )

    result = params.to_dict()

    assert "family" in result
    assert "given" not in result
    assert "identifier" not in result


def test_all_new_params_practitioner():
    """Test tous les nouveaux paramètres Practitioner."""
    params = PractitionerSearchParams(
        family="Test",
        active=True,
        id="123",
        last_updated="ge2025-01-01",
        data_information_system="RPPS",
        identifier_type="8",
        mailbox_mss="test@mssante.fr",
        number_smartcard="123456789",
        qualification_code="SM26",
    )

    result = params.to_dict()

    assert result["_id"] == "123"
    assert result["_lastUpdated"] == "ge2025-01-01"
    assert result["data-information-system"] == "RPPS"
    assert result["identifier-type"] == "8"
    assert result["mailbox-mss"] == "test@mssante.fr"
    assert result["number-smartcard"] == "123456789"
    assert result["qualification-code"] == "SM26"
