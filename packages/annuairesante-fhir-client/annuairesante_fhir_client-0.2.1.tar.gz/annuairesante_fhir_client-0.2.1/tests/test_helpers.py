"""Tests pour les helpers."""

import pytest

from annuairesante_fhir.helpers import wrap_organization, wrap_practitioner
from annuairesante_fhir.sub_helpers import IdentifierHelper


def test_identifier_helper_finess():
    """Test extraction FINESS."""
    id_data = {
        "type": {
            "coding": [
                {
                    "system": "https://hl7.fr/ig/fhir/core/CodeSystem/fr-core-cs-v2-0203",
                    "code": "FINEJ",
                }
            ]
        },
        "value": "970208906",
    }

    helper = IdentifierHelper(id_data, resolve_mos=False)

    assert helper.type_code == "FINEJ"
    assert helper.value == "970208906"
    assert helper.is_finess is True
    assert helper.is_finej is True
    assert helper.is_fineg is False


def test_identifier_helper_fineg():
    """Test extraction FINEG."""
    id_data = {
        "type": {
            "coding": [
                {
                    "system": "https://hl7.fr/ig/fhir/core/CodeSystem/fr-core-cs-v2-0203",
                    "code": "FINEG",
                }
            ]
        },
        "value": "970200028",
    }

    helper = IdentifierHelper(id_data, resolve_mos=False)

    assert helper.type_code == "FINEG"
    assert helper.is_finess is True
    assert helper.is_fineg is True
    assert helper.is_finej is False


def test_identifier_helper_rpps():
    """Test extraction RPPS."""
    id_data = {
        "type": {
            "coding": [
                {
                    "system": "https://hl7.fr/ig/fhir/core/CodeSystem/fr-core-cs-v2-0203",
                    "code": "RPPS",
                }
            ]
        },
        "value": "10000000000",
    }

    helper = IdentifierHelper(id_data, resolve_mos=False)

    assert helper.type_code == "RPPS"
    assert helper.is_rpps is True
    assert helper.is_adeli is False


def test_organization_helper_finess_extraction():
    """Test extraction FINESS depuis Organization."""
    org_data = {
        "resourceType": "Organization",
        "id": "001-02-67283",
        "identifier": [
            {
                "type": {
                    "coding": [
                        {
                            "system": "https://hl7.fr/ig/fhir/core/CodeSystem/fr-core-cs-v2-0203",
                            "code": "FINEJ",
                        }
                    ]
                },
                "value": "970208906",
            }
        ],
        "name": "CHI LORRAIN BASSE POINTE",
    }

    org = wrap_organization(org_data)

    assert org.id == "001-02-67283"
    assert org.name == "CHI LORRAIN BASSE POINTE"
    assert org.finess == "970208906"
    assert org.finej == "970208906"
    assert org.fineg is None


def test_practitioner_helper_rpps_extraction():
    """Test extraction RPPS depuis Practitioner."""
    prac_data = {
        "resourceType": "Practitioner",
        "id": "001-123456",
        "identifier": [
            {
                "type": {
                    "coding": [
                        {
                            "system": "https://hl7.fr/ig/fhir/core/CodeSystem/fr-core-cs-v2-0203",
                            "code": "RPPS",
                        }
                    ]
                },
                "value": "10001234567",
            }
        ],
        "name": [{"family": "Dupont", "given": ["Jean"]}],
    }

    prac = wrap_practitioner(prac_data)

    assert prac.id == "001-123456"
    assert prac.rpps == "10001234567"
    # Les noms sont dans names (liste de NameHelper)
    assert len(prac.names) > 0
    assert prac.names[0].family == "Dupont"
    assert prac.names[0].given == ["Jean"]
