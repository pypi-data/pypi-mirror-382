"""Models and types for Annuaire Santé FHIR client."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SearchParams(BaseModel):
    """Base model for FHIR search parameters.

    Note: Annuaire Santé API does not support _count and _offset parameters.
    Pagination is handled via 'next' links in Bundle responses.
    """

    model_config = ConfigDict(populate_by_name=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values, using aliases."""
        return {k: v for k, v in self.model_dump(by_alias=True).items() if v is not None}


class PractitionerSearchParams(SearchParams):
    """Search parameters for Practitioner resource."""

    # Paramètres de base
    family: Optional[str] = Field(None, description="Nom de famille")
    given: Optional[str] = Field(None, description="Prénom")
    identifier: Optional[str] = Field(None, description="Identifiant (RPPS, ADELI, etc.)")
    name: Optional[str] = Field(None, description="Nom complet")
    telecom: Optional[str] = Field(None, description="Email ou téléphone")

    # Paramètres standards FHIR
    active: Optional[bool] = Field(None, description="Statut d'exercice (ouvert/fermé)")
    id: Optional[str] = Field(None, alias="_id", description="ID technique de la ressource")
    last_updated: Optional[str] = Field(
        None, alias="_lastUpdated", description="Date de dernière mise à jour"
    )

    # Paramètres spécifiques Annuaire Santé
    data_information_system: Optional[str] = Field(
        None,
        alias="data-information-system",
        description="Système d'information (RPPS, ADELI, etc.)",
    )
    identifier_type: Optional[str] = Field(
        None, alias="identifier-type", description="Type d'identifiant"
    )
    mailbox_mss: Optional[str] = Field(
        None, alias="mailbox-mss", description="Boîte de messagerie sécurisée"
    )
    number_smartcard: Optional[str] = Field(
        None, alias="number-smartcard", description="Numéro de carte CPS/CPF"
    )
    qualification_code: Optional[str] = Field(
        None, alias="qualification-code", description="Code de qualification/diplôme"
    )


class OrganizationSearchParams(SearchParams):
    """Search parameters for Organization resource."""

    # Paramètres de base
    name: Optional[str] = Field(None, description="Nom de l'organisation")
    identifier: Optional[str] = Field(None, description="Identifiant (FINESS, SIRET, etc.)")
    type: Optional[str] = Field(None, description="Type d'organisation")
    address: Optional[str] = Field(None, description="Adresse")
    address_city: Optional[str] = Field(None, alias="address-city", description="Ville")
    address_postalcode: Optional[str] = Field(
        None, alias="address-postalcode", description="Code postal"
    )

    # Paramètres standards FHIR
    active: Optional[bool] = Field(None, description="Statut de l'organisation")
    id: Optional[str] = Field(None, alias="_id", description="ID technique de la ressource")
    last_updated: Optional[str] = Field(
        None, alias="_lastUpdated", description="Date de dernière mise à jour"
    )

    # Paramètres spécifiques Annuaire Santé
    data_information_system: Optional[str] = Field(
        None, alias="data-information-system", description="Système d'information"
    )
    identifier_type: Optional[str] = Field(
        None, alias="identifier-type", description="Type d'identifiant"
    )
    mailbox_mss: Optional[str] = Field(
        None, alias="mailbox-mss", description="Boîtes de messagerie sécurisée"
    )
    partof: Optional[str] = Field(
        None, description="Établissements géographiques d'une entité juridique"
    )
    pharmacy_licence: Optional[str] = Field(
        None, alias="pharmacy-licence", description="Numéro de licence de pharmacie"
    )


class PractitionerRoleSearchParams(SearchParams):
    """Search parameters for PractitionerRole resource."""

    # Paramètres de base
    practitioner: Optional[str] = Field(None, description="Référence au Practitioner")
    organization: Optional[str] = Field(None, description="Référence à l'Organization")
    role: Optional[str] = Field(None, description="Code de rôle")
    specialty: Optional[str] = Field(None, description="Code de spécialité")
    active: Optional[bool] = Field(None, description="Statut actif")

    # Paramètres standards FHIR
    id: Optional[str] = Field(None, alias="_id", description="ID technique de la ressource")
    last_updated: Optional[str] = Field(
        None, alias="_lastUpdated", description="Date de dernière mise à jour"
    )

    # Paramètres spécifiques Annuaire Santé
    identifier: Optional[str] = Field(None, description="Identifiant du professionnel")
    data_information_system: Optional[str] = Field(
        None, alias="data-information-system", description="Système d'information"
    )
    data_registration_authority: Optional[str] = Field(
        None, alias="data-registration-authority", description="Autorité d'enregistrement"
    )
    mailbox_mss: Optional[str] = Field(
        None, alias="mailbox-mss", description="Boîte MSS de la structure"
    )


class HealthcareServiceSearchParams(SearchParams):
    """Search parameters for HealthcareService resource."""

    # Paramètres de base
    name: Optional[str] = Field(None, description="Nom du service")
    organization: Optional[str] = Field(None, description="Référence à l'Organization")
    service_type: Optional[str] = Field(
        None, alias="service-type", description="Type de service/discipline"
    )
    active: Optional[bool] = Field(None, description="Statut actif")

    # Paramètres standards FHIR
    id: Optional[str] = Field(None, alias="_id", description="ID technique de la ressource")
    last_updated: Optional[str] = Field(
        None, alias="_lastUpdated", description="Date de dernière mise à jour"
    )
    profile: Optional[str] = Field(None, alias="_profile", description="Profil spécifique")

    # Paramètres spécifiques Annuaire Santé
    identifier: Optional[str] = Field(None, description="Identifiant spécifique")
    characteristic: Optional[str] = Field(None, description="Forme d'activité")
    service_category: Optional[str] = Field(
        None, alias="service-category", description="Modalité du service de santé"
    )


class DeviceSearchParams(SearchParams):
    """Search parameters for Device resource."""

    # Paramètres de base
    identifier: Optional[str] = Field(None, description="Identifiant de l'équipement (ARHGOS)")
    type: Optional[str] = Field(None, description="Type d'équipement matériel lourd")
    status: Optional[str] = Field(None, description="Statut de l'équipement")
    organization: Optional[str] = Field(None, description="Référence à l'Organization")

    # Paramètres standards FHIR
    id: Optional[str] = Field(None, alias="_id", description="ID technique de la ressource")
    last_updated: Optional[str] = Field(
        None, alias="_lastUpdated", description="Date de dernière mise à jour"
    )

    # Paramètres spécifiques Annuaire Santé
    manufacturer: Optional[str] = Field(None, description="Marque de l'équipement")
    model: Optional[str] = Field(None, description="Modèle de l'équipement")
    data_information_system: Optional[str] = Field(
        None, alias="data-information-system", description="Système d'information"
    )


class BundleResponse(BaseModel):
    """Response wrapper for FHIR Bundle."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    total: int = Field(description="Total number of results")
    entries: List[Any] = Field(default_factory=list, description="List of resources")
    next_url: Optional[str] = Field(None, description="URL for next page")
