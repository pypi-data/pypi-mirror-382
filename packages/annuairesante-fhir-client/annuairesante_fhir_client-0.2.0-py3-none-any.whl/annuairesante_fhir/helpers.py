"""Helpers pour accéder facilement aux données des ressources FHIR."""

from typing import Any, Dict, List, Optional

from annuairesante_fhir.mos_resolver import MOSResolver
from annuairesante_fhir.sub_helpers import (
    AddressHelper,
    AuthorizationHelper,
    IdentifierHelper,
    NameHelper,
    QualificationHelper,
    SmartcardHelper,
    TelecomHelper,
)

# Instance partagée du résolveur MOS
_mos_resolver = None


def get_mos_resolver() -> MOSResolver:
    """Retourne l'instance partagée du MOSResolver."""
    global _mos_resolver
    if _mos_resolver is None:
        _mos_resolver = MOSResolver()
    return _mos_resolver


class PractitionerHelper:
    """Helper pour accéder facilement aux données d'un Practitioner."""

    def __init__(self, data: Dict[str, Any]):
        """
        Args:
            data: Dictionnaire JSON du Practitioner
        """
        self._data = data

    @property
    def id(self) -> Optional[str]:
        """ID du practitioner."""
        return self._data.get("id")

    @property
    def resource_type(self) -> Optional[str]:
        """Type de ressource FHIR."""
        return self._data.get("resourceType")

    @property
    def active(self) -> Optional[bool]:
        """Statut actif."""
        return self._data.get("active")

    @property
    def language(self) -> Optional[str]:
        """Langue de la ressource."""
        return self._data.get("language")

    # Métadonnées
    @property
    def meta_version_id(self) -> Optional[int]:
        """Version ID des métadonnées."""
        meta = self._data.get("meta", {})
        return meta.get("versionId")

    @property
    def meta_last_updated(self) -> Optional[str]:
        """Date de dernière mise à jour."""
        meta = self._data.get("meta", {})
        return meta.get("lastUpdated")

    @property
    def meta_source(self) -> Optional[str]:
        """Source des données."""
        meta = self._data.get("meta", {})
        return meta.get("source")

    @property
    def meta_profiles(self) -> List[str]:
        """Profils FHIR appliqués."""
        meta = self._data.get("meta", {})
        return meta.get("profile", [])

    @property
    def data_trace_system(self) -> Optional[str]:
        """Système d'information source (RPPS, ADELI, etc.)."""
        meta = self._data.get("meta", {})
        extensions = meta.get("extension", [])
        for ext in extensions:
            if "data-trace" in ext.get("url", ""):
                sub_extensions = ext.get("extension", [])
                for sub_ext in sub_extensions:
                    if sub_ext.get("url") == "systeme-information":
                        return sub_ext.get("valueCode")
        return None

    # Informations personnelles
    @property
    def gender(self) -> Optional[str]:
        """Genre (male, female, other, unknown)."""
        return self._data.get("gender")

    @property
    def birth_date(self) -> Optional[str]:
        """Date de naissance."""
        return self._data.get("birthDate")

    @property
    def deceased(self) -> Optional[bool]:
        """Indique si le praticien est décédé."""
        deceased = self._data.get("deceasedBoolean")
        if deceased is not None:
            return deceased
        return self._data.get("deceasedDateTime") is not None

    @property
    def deceased_date(self) -> Optional[str]:
        """Date de décès."""
        return self._data.get("deceasedDateTime")

    # Noms
    @property
    def names(self) -> List[NameHelper]:
        """Liste de tous les noms avec helpers."""
        names = self._data.get("name", [])
        return [NameHelper(name_data) for name_data in names]

    @property
    def name(self) -> Optional[str]:
        """Nom complet."""
        names = self._data.get("name", [])
        if names:
            name_helper = NameHelper(names[0])
            return name_helper.full_name
        return None

    @property
    def family(self) -> Optional[str]:
        """Nom de famille."""
        names = self._data.get("name", [])
        if names:
            return names[0].get("family")
        return None

    @property
    def given(self) -> Optional[str]:
        """Prénom(s)."""
        names = self._data.get("name", [])
        if names:
            given_list = names[0].get("given", [])
            return " ".join(given_list) if given_list else None
        return None

    @property
    def prefix(self) -> Optional[str]:
        """Civilité (Dr, M., Mme, etc.)."""
        names = self._data.get("name", [])
        if names:
            prefix_list = names[0].get("prefix", [])
            return " ".join(prefix_list) if prefix_list else None
        return None

    @property
    def suffix(self) -> Optional[str]:
        """Suffixes du nom."""
        names = self._data.get("name", [])
        if names:
            suffix_list = names[0].get("suffix", [])
            return " ".join(suffix_list) if suffix_list else None
        return None

    # Identifiants
    @property
    def rpps(self) -> Optional[str]:
        """Numéro RPPS."""
        identifiers = self._data.get("identifier", [])
        for id_data in identifiers:
            id_helper = IdentifierHelper(id_data, resolve_mos=False)
            if id_helper.is_rpps:
                return id_helper.value
        return None

    @property
    def adeli(self) -> Optional[str]:
        """Numéro ADELI."""
        identifiers = self._data.get("identifier", [])
        for id_data in identifiers:
            id_helper = IdentifierHelper(id_data, resolve_mos=False)
            if id_helper.is_adeli:
                return id_helper.value
        return None

    @property
    def idnps(self) -> Optional[str]:
        """Identifiant National des Professionnels de Santé."""
        identifiers = self._data.get("identifier", [])
        for id_data in identifiers:
            id_helper = IdentifierHelper(id_data, resolve_mos=False)
            if id_helper.is_idnps:
                return id_helper.value
        return None

    @property
    def identifiers(self) -> List[IdentifierHelper]:
        """Liste de tous les identifiants avec helpers."""
        identifiers = self._data.get("identifier", [])
        return [IdentifierHelper(id_data, resolve_mos=True) for id_data in identifiers]

    # Adresses
    @property
    def addresses(self) -> List[AddressHelper]:
        """Liste de toutes les adresses avec helpers."""
        addresses = self._data.get("address", [])
        return [AddressHelper(addr_data) for addr_data in addresses]

    @property
    def address(self) -> Optional[str]:
        """Adresse formatée."""
        addresses = self._data.get("address", [])
        if addresses:
            addr_helper = AddressHelper(addresses[0])
            return addr_helper.full_address
        return None

    @property
    def city(self) -> Optional[str]:
        """Ville."""
        addresses = self._data.get("address", [])
        if addresses:
            return addresses[0].get("city")
        return None

    @property
    def postal_code(self) -> Optional[str]:
        """Code postal."""
        addresses = self._data.get("address", [])
        if addresses:
            return addresses[0].get("postalCode")
        return None

    # Télécoms
    @property
    def phone(self) -> Optional[str]:
        """Téléphone."""
        telecoms = self._data.get("telecom", [])
        for telecom_data in telecoms:
            telecom = TelecomHelper(telecom_data)
            if telecom.is_phone:
                return telecom.value
        return None

    @property
    def email(self) -> Optional[str]:
        """Email (non MSSanté)."""
        telecoms = self._data.get("telecom", [])
        for telecom_data in telecoms:
            telecom = TelecomHelper(telecom_data)
            if telecom.is_email and not telecom.is_mssante:
                return telecom.value
        return None

    @property
    def mssante_emails(self) -> List[TelecomHelper]:
        """Liste des emails MSSanté."""
        telecoms = self._data.get("telecom", [])
        helpers = [TelecomHelper(t) for t in telecoms]
        return [h for h in helpers if h.is_mssante]

    @property
    def telecoms(self) -> List[TelecomHelper]:
        """Liste de tous les moyens de contact avec helpers."""
        telecoms = self._data.get("telecom", [])
        return [TelecomHelper(telecom_data) for telecom_data in telecoms]

    # Qualifications
    @property
    def qualifications(self) -> List[QualificationHelper]:
        """Liste des qualifications avec helpers."""
        qualifications = self._data.get("qualification", [])
        return [QualificationHelper(qual_data, resolve_mos=True) for qual_data in qualifications]

    @property
    def main_profession(self) -> Optional[str]:
        """Profession principale (première qualification de type profession)."""
        for qual in self.qualifications:
            if qual.type == "profession":
                return qual.profession_display or qual.profession
        return None

    @property
    def main_diploma(self) -> Optional[str]:
        """Diplôme principal (première qualification de type diplôme)."""
        for qual in self.qualifications:
            if qual.type == "diplome":
                return qual.diplome_display or qual.diplome
        return None

    # Communications (langues parlées)
    @property
    def communications(self) -> List[Dict[str, Any]]:
        """Langues de communication.

        Returns:
            Liste de dictionnaires avec 'code', 'system', 'display'
        """
        result = []
        communications = self._data.get("communication", [])
        resolver = get_mos_resolver()
        for comm in communications:
            # La structure est communication.language.coding
            language = comm.get("language", {})
            codings = language.get("coding", [])
            if codings:
                coding = codings[0]  # Prendre le premier coding
                code = coding.get("code")
                system = coding.get("system")
                display = coding.get("display")

                # Résoudre le code MOS si display n'est pas fourni
                if not display and code and system:
                    display = resolver.resolve(system, code)

                result.append({"system": system, "code": code, "display": display})
        return result

    # Carte professionnelle
    @property
    def smartcard(self) -> Optional[SmartcardHelper]:
        """Informations sur la carte CPS/CPF."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if "smartcard" in ext.get("url", ""):
                return SmartcardHelper(ext)
        return None

    @property
    def smartcards(self) -> List[SmartcardHelper]:
        """Liste de toutes les cartes professionnelles."""
        extensions = self._data.get("extension", [])
        return [SmartcardHelper(ext) for ext in extensions if "smartcard" in ext.get("url", "")]

    # Photo
    @property
    def photo_url(self) -> Optional[str]:
        """URL de la photo du praticien."""
        photos = self._data.get("photo", [])
        if photos:
            return photos[0].get("url")
        return None

    @property
    def photo_data(self) -> Optional[str]:
        """Données de la photo en base64."""
        photos = self._data.get("photo", [])
        if photos:
            return photos[0].get("data")
        return None

    @property
    def raw(self) -> Dict[str, Any]:
        """Données brutes JSON."""
        return self._data

    def __repr__(self) -> str:
        return f"<Practitioner {self.name} (RPPS: {self.rpps})>"


class OrganizationHelper:
    """Helper pour accéder facilement aux données d'une Organization."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def id(self) -> Optional[str]:
        """ID de l'organisation."""
        return self._data.get("id")

    @property
    def resource_type(self) -> Optional[str]:
        """Type de ressource FHIR."""
        return self._data.get("resourceType")

    @property
    def name(self) -> Optional[str]:
        """Nom de l'organisation."""
        return self._data.get("name")

    @property
    def active(self) -> Optional[bool]:
        """Statut actif."""
        return self._data.get("active")

    @property
    def language(self) -> Optional[str]:
        """Langue de la ressource."""
        return self._data.get("language")

    # Métadonnées
    @property
    def meta_version_id(self) -> Optional[int]:
        """Version ID des métadonnées."""
        meta = self._data.get("meta", {})
        return meta.get("versionId")

    @property
    def meta_last_updated(self) -> Optional[str]:
        """Date de dernière mise à jour."""
        meta = self._data.get("meta", {})
        return meta.get("lastUpdated")

    @property
    def meta_source(self) -> Optional[str]:
        """Source des données."""
        meta = self._data.get("meta", {})
        return meta.get("source")

    @property
    def meta_profiles(self) -> List[str]:
        """Profils FHIR appliqués."""
        meta = self._data.get("meta", {})
        return meta.get("profile", [])

    @property
    def data_trace_system(self) -> Optional[str]:
        """Système d'information source (FINESS, etc.)."""
        meta = self._data.get("meta", {})
        extensions = meta.get("extension", [])
        for ext in extensions:
            if "data-trace" in ext.get("url", ""):
                sub_extensions = ext.get("extension", [])
                for sub_ext in sub_extensions:
                    if sub_ext.get("url") == "systeme-information":
                        return sub_ext.get("valueCode")
        return None

    # Identifiants
    @property
    def finess(self) -> Optional[str]:
        """Numéro FINESS (priorité FINEJ puis FINEG)."""
        identifiers = self._data.get("identifier", [])
        # Prioriser FINEJ (juridique)
        for id_data in identifiers:
            id_helper = IdentifierHelper(id_data, resolve_mos=False)
            if id_helper.is_finej:
                return id_helper.value
        # Sinon FINEG (géographique)
        for id_data in identifiers:
            id_helper = IdentifierHelper(id_data, resolve_mos=False)
            if id_helper.is_fineg:
                return id_helper.value
        return None

    @property
    def finej(self) -> Optional[str]:
        """Numéro FINEJ (FINESS juridique)."""
        identifiers = self._data.get("identifier", [])
        for id_data in identifiers:
            id_helper = IdentifierHelper(id_data, resolve_mos=False)
            if id_helper.is_finej:
                return id_helper.value
        return None

    @property
    def fineg(self) -> Optional[str]:
        """Numéro FINEG (FINESS géographique)."""
        identifiers = self._data.get("identifier", [])
        for id_data in identifiers:
            id_helper = IdentifierHelper(id_data, resolve_mos=False)
            if id_helper.is_fineg:
                return id_helper.value
        return None

    @property
    def idnst(self) -> Optional[str]:
        """Identifiant National de Structure."""
        identifiers = self._data.get("identifier", [])
        for id_data in identifiers:
            id_helper = IdentifierHelper(id_data, resolve_mos=False)
            if id_helper.is_idnst:
                return id_helper.value
        return None

    @property
    def siret(self) -> Optional[str]:
        """Numéro SIRET."""
        identifiers = self._data.get("identifier", [])
        for id_data in identifiers:
            id_helper = IdentifierHelper(id_data, resolve_mos=False)
            if id_helper.is_siret:
                return id_helper.value
        return None

    @property
    def identifiers(self) -> List[IdentifierHelper]:
        """Liste de tous les identifiants avec helpers."""
        identifiers = self._data.get("identifier", [])
        return [IdentifierHelper(id_data, resolve_mos=True) for id_data in identifiers]

    # Période d'activité
    @property
    def period_start(self) -> Optional[str]:
        """Date de début d'activité."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if "organization-period" in ext.get("url", ""):
                period = ext.get("valuePeriod", {})
                return period.get("start")
        return None

    @property
    def period_end(self) -> Optional[str]:
        """Date de fin d'activité."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if "organization-period" in ext.get("url", ""):
                period = ext.get("valuePeriod", {})
                return period.get("end")
        return None

    # Types d'organisation
    @property
    def types(self) -> List[Dict[str, Any]]:
        """Types d'organisation avec codes MOS et extensions.

        Returns:
            Liste de dictionnaires avec 'code', 'system', 'display', 'organization_type'
        """
        result: List[Dict[str, Any]] = []
        types = self._data.get("type", [])
        resolver = get_mos_resolver()
        for org_type in types:
            # Récupérer le type d'organisation depuis l'extension
            org_type_value = None
            extensions = org_type.get("extension", [])
            for ext in extensions:
                if "organization-types" in ext.get("url", ""):
                    org_type_value = ext.get("valueCode")

            codings = org_type.get("coding", [])
            if codings:
                coding = codings[0]  # Prendre le premier coding
                code = coding.get("code")
                system = coding.get("system")
                display = coding.get("display")

                # Résoudre le code MOS si display n'est pas fourni
                if not display and code and system:
                    display = resolver.resolve(system, code)

                result.append(
                    {
                        "system": system,
                        "code": code,
                        "display": display,
                        "organization_type": org_type_value,
                    }
                )
        return result

    @property
    def organization_type(self) -> Optional[str]:
        """Type principal d'organisation (organizationType)."""
        for type_info in self.types:
            if type_info.get("organization_type") == "organizationType":
                return type_info.get("code")
        return None

    @property
    def secteur_activite_rass(self) -> Optional[str]:
        """Secteur d'activité RASS."""
        for type_info in self.types:
            if type_info.get("organization_type") == "secteurActiviteRASS":
                return type_info.get("code")
        return None

    @property
    def categorie_etablissement(self) -> Optional[str]:
        """Catégorie d'établissement."""
        for type_info in self.types:
            if "CategorieEtablissement" in (type_info.get("system") or ""):
                return type_info.get("code")
        return None

    @property
    def activite_insee(self) -> Optional[str]:
        """Activité INSEE (code NAF)."""
        for type_info in self.types:
            if type_info.get("organization_type") == "activiteINSEE":
                return type_info.get("code")
        return None

    @property
    def sph_participation(self) -> Optional[str]:
        """Participation au service public hospitalier."""
        for type_info in self.types:
            if type_info.get("organization_type") == "sphParticipation":
                return type_info.get("code")
        return None

    # Adresses
    @property
    def addresses(self) -> List[AddressHelper]:
        """Liste de toutes les adresses avec helpers."""
        addresses = self._data.get("address", [])
        return [AddressHelper(addr_data) for addr_data in addresses]

    @property
    def address(self) -> Optional[str]:
        """Adresse formatée."""
        addresses = self._data.get("address", [])
        if addresses:
            addr_helper = AddressHelper(addresses[0])
            return addr_helper.full_address
        return None

    @property
    def city(self) -> Optional[str]:
        """Ville."""
        addresses = self._data.get("address", [])
        if addresses:
            return addresses[0].get("city")
        return None

    @property
    def district(self) -> Optional[str]:
        """District/Département."""
        addresses = self._data.get("address", [])
        if addresses:
            return addresses[0].get("district")
        return None

    @property
    def postal_code(self) -> Optional[str]:
        """Code postal."""
        addresses = self._data.get("address", [])
        if addresses:
            return addresses[0].get("postalCode")
        return None

    @property
    def insee_code(self) -> Optional[str]:
        """Code INSEE de la commune."""
        if self.addresses:
            return self.addresses[0].insee_code
        return None

    # Télécoms
    @property
    def phone(self) -> Optional[str]:
        """Téléphone."""
        telecoms = self._data.get("telecom", [])
        for telecom_data in telecoms:
            telecom = TelecomHelper(telecom_data)
            if telecom.is_phone:
                return telecom.value
        return None

    @property
    def email(self) -> Optional[str]:
        """Email (non MSSanté)."""
        telecoms = self._data.get("telecom", [])
        for telecom_data in telecoms:
            telecom = TelecomHelper(telecom_data)
            if telecom.is_email and not telecom.is_mssante:
                return telecom.value
        return None

    @property
    def mssante_emails(self) -> List[TelecomHelper]:
        """Liste des emails MSSanté."""
        telecoms = self._data.get("telecom", [])
        helpers = [TelecomHelper(t) for t in telecoms]
        return [h for h in helpers if h.is_mssante]

    @property
    def telecoms(self) -> List[TelecomHelper]:
        """Liste de tous les moyens de contact avec helpers."""
        telecoms = self._data.get("telecom", [])
        return [TelecomHelper(telecom_data) for telecom_data in telecoms]

    # Organisation parente
    @property
    def parent_id(self) -> Optional[str]:
        """ID de l'organisation parente."""
        part_of = self._data.get("partOf", {})
        ref = part_of.get("reference")
        return ref.split("/")[-1] if ref else None

    @property
    def raw(self) -> Dict[str, Any]:
        """Données brutes JSON."""
        return self._data

    def __repr__(self) -> str:
        return f"<Organization {self.name} (FINESS: {self.finess})>"


class PractitionerRoleHelper:
    """Helper pour accéder facilement aux données d'un PractitionerRole."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def id(self) -> Optional[str]:
        """ID du role."""
        return self._data.get("id")

    @property
    def active(self) -> Optional[bool]:
        """Statut actif."""
        return self._data.get("active")

    @property
    def practitioner_id(self) -> Optional[str]:
        """ID du practitioner."""
        practitioner = self._data.get("practitioner", {})
        ref = practitioner.get("reference")
        return ref.split("/")[-1] if ref else None

    @property
    def organization_id(self) -> Optional[str]:
        """ID de l'organisation."""
        organization = self._data.get("organization", {})
        ref = organization.get("reference")
        return ref.split("/")[-1] if ref else None

    @property
    def roles(self) -> List[Dict[str, str]]:
        """Rôles avec codes MOS.

        Returns:
            Liste de dictionnaires avec 'code', 'system', 'display'
        """
        result: List[Dict[str, str]] = []
        roles = self._data.get("code", [])
        resolver = get_mos_resolver()
        for role in roles:
            codings = role.get("coding", [])
            if codings:
                coding = codings[0]  # Prendre le premier coding
                code = coding.get("code")
                system = coding.get("system")
                display = coding.get("display")

                # Résoudre le code MOS si display n'est pas fourni
                if not display and code and system:
                    display = resolver.resolve(system, code)

                result.append({"code": code, "system": system, "display": display})
        return result

    @property
    def specialties(self) -> List[Dict[str, str]]:
        """Spécialités avec codes MOS.

        Returns:
            Liste de dictionnaires avec 'code', 'system', 'display'
        """
        result: List[Dict[str, str]] = []
        specialties = self._data.get("specialty", [])
        resolver = get_mos_resolver()
        for specialty in specialties:
            codings = specialty.get("coding", [])
            if codings:
                coding = codings[0]  # Prendre le premier coding
                code = coding.get("code")
                system = coding.get("system")
                display = coding.get("display")

                # Résoudre le code MOS si display n'est pas fourni
                if not display and code and system:
                    display = resolver.resolve(system, code)

                result.append({"code": code, "system": system, "display": display})
        return result

    @property
    def period(self) -> Optional[Dict[str, str]]:
        """Période d'activité."""
        period = self._data.get("period")
        if period:
            return {"start": period.get("start"), "end": period.get("end")}
        return None

    @property
    def raw(self) -> Dict[str, Any]:
        """Données brutes JSON."""
        return self._data

    def __repr__(self) -> str:
        return f"<PractitionerRole {self.id}>"


def wrap_practitioner(data: Dict[str, Any]) -> PractitionerHelper:
    """Enveloppe un Practitioner dans un helper."""
    return PractitionerHelper(data)


def wrap_organization(data: Dict[str, Any]) -> OrganizationHelper:
    """Enveloppe une Organization dans un helper."""
    return OrganizationHelper(data)


def wrap_practitioner_role(data: Dict[str, Any]) -> PractitionerRoleHelper:
    """Enveloppe un PractitionerRole dans un helper."""
    return PractitionerRoleHelper(data)


class HealthcareServiceHelper:
    """Helper pour accéder facilement aux données d'un HealthcareService."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def id(self) -> Optional[str]:
        """ID du service."""
        return self._data.get("id")

    @property
    def resource_type(self) -> Optional[str]:
        """Type de ressource FHIR."""
        return self._data.get("resourceType")

    @property
    def active(self) -> Optional[bool]:
        """Statut actif."""
        return self._data.get("active")

    @property
    def language(self) -> Optional[str]:
        """Langue de la ressource."""
        return self._data.get("language")

    # Métadonnées
    @property
    def meta_version_id(self) -> Optional[str]:
        """Version ID des métadonnées."""
        meta = self._data.get("meta", {})
        return meta.get("versionId")

    @property
    def meta_last_updated(self) -> Optional[str]:
        """Date de dernière mise à jour."""
        meta = self._data.get("meta", {})
        return meta.get("lastUpdated")

    @property
    def meta_source(self) -> Optional[str]:
        """Source des données."""
        meta = self._data.get("meta", {})
        return meta.get("source")

    # Identifiants
    @property
    def identifiers(self) -> List[IdentifierHelper]:
        """Liste de tous les identifiants avec helpers."""
        identifiers = self._data.get("identifier", [])
        return [IdentifierHelper(id_data, resolve_mos=False) for id_data in identifiers]

    @property
    def arhgos_id(self) -> Optional[str]:
        """Identifiant ARHGOS."""
        identifiers = self._data.get("identifier", [])
        for id_data in identifiers:
            system = id_data.get("system", "")
            if "arhgos" in system.lower():
                return id_data.get("value")
        return None

    # Nom
    @property
    def name(self) -> Optional[str]:
        """Nom du service."""
        return self._data.get("name")

    # Organisation
    @property
    def organization_id(self) -> Optional[str]:
        """ID de l'organisation qui fournit le service."""
        provided_by = self._data.get("providedBy", {})
        ref = provided_by.get("reference")
        return ref.split("/")[-1] if ref else None

    # Autorisation
    @property
    def authorization(self) -> Optional[AuthorizationHelper]:
        """Autorisation du service."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if "authorization" in ext.get("url", "").lower():
                return AuthorizationHelper(ext)
        return None

    # Catégorie
    @property
    def categories(self) -> List[Dict]:
        """Catégories du service (modalité d'activité).

        Returns:
            Liste de dictionnaires avec 'code', 'system', 'display'
        """
        result = []
        categories = self._data.get("category", [])
        resolver = get_mos_resolver()
        for category in categories:
            codings = category.get("coding", [])
            if codings:
                coding = codings[0]  # Prendre le premier coding
                code = coding.get("code")
                system = coding.get("system")
                display = coding.get("display")

                # Résoudre le code MOS si display n'est pas fourni
                if not display and code and system:
                    display = resolver.resolve(system, code)

                result.append({"code": code, "system": system, "display": display})
        return result

    # Types
    @property
    def types(self) -> List[Dict]:
        """Types d'activité du service.

        Returns:
            Liste de dictionnaires avec 'code', 'system', 'display'
        """
        result = []
        types = self._data.get("type", [])
        resolver = get_mos_resolver()
        for service_type in types:
            codings = service_type.get("coding", [])
            if codings:
                coding = codings[0]  # Prendre le premier coding
                code = coding.get("code")
                system = coding.get("system")
                display = coding.get("display")

                # Résoudre le code MOS si display n'est pas fourni
                if not display and code and system:
                    display = resolver.resolve(system, code)

                result.append({"code": code, "system": system, "display": display})
        return result

    # Caractéristiques
    @property
    def characteristics(self) -> List[Dict]:
        """Caractéristiques du service (forme d'activité).

        Returns:
            Liste de dictionnaires avec 'code', 'system', 'display'
        """
        result = []
        characteristics = self._data.get("characteristic", [])
        resolver = get_mos_resolver()
        for characteristic in characteristics:
            codings = characteristic.get("coding", [])
            if codings:
                coding = codings[0]  # Prendre le premier coding
                code = coding.get("code")
                system = coding.get("system")
                display = coding.get("display")

                # Résoudre le code MOS si display n'est pas fourni
                if not display and code and system:
                    display = resolver.resolve(system, code)

                result.append({"code": code, "system": system, "display": display})
        return result

    @property
    def raw(self) -> Dict[str, Any]:
        """Données brutes JSON."""
        return self._data

    def __repr__(self) -> str:
        return f"<HealthcareService {self.name or self.id}>"


class DeviceHelper:
    """Helper pour accéder facilement aux données d'un Device."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def id(self) -> Optional[str]:
        """ID du device."""
        return self._data.get("id")

    @property
    def resource_type(self) -> Optional[str]:
        """Type de ressource FHIR."""
        return self._data.get("resourceType")

    @property
    def status(self) -> Optional[str]:
        """Statut du device (active, inactive, etc.)."""
        return self._data.get("status")

    @property
    def language(self) -> Optional[str]:
        """Langue de la ressource."""
        return self._data.get("language")

    # Métadonnées
    @property
    def meta_version_id(self) -> Optional[str]:
        """Version ID des métadonnées."""
        meta = self._data.get("meta", {})
        return meta.get("versionId")

    @property
    def meta_last_updated(self) -> Optional[str]:
        """Date de dernière mise à jour."""
        meta = self._data.get("meta", {})
        return meta.get("lastUpdated")

    @property
    def meta_source(self) -> Optional[str]:
        """Source des données."""
        meta = self._data.get("meta", {})
        return meta.get("source")

    # Identifiants
    @property
    def identifiers(self) -> List[IdentifierHelper]:
        """Liste de tous les identifiants avec helpers."""
        identifiers = self._data.get("identifier", [])
        return [IdentifierHelper(id_data, resolve_mos=False) for id_data in identifiers]

    @property
    def arhgos_id(self) -> Optional[str]:
        """Identifiant ARHGOS."""
        identifiers = self._data.get("identifier", [])
        for id_data in identifiers:
            system = id_data.get("system", "")
            if "arhgos" in system.lower():
                return id_data.get("value")
        return None

    # Fabricant
    @property
    def manufacturer(self) -> Optional[str]:
        """Fabricant du device."""
        return self._data.get("manufacturer")

    # Type
    @property
    def device_type(self) -> Optional[Dict[str, str]]:
        """Type d'équipement matériel lourd."""
        device_type = self._data.get("type", {})
        if device_type:
            codings = device_type.get("coding", [])
            if codings:
                coding = codings[0]
                code = coding.get("code")
                system = coding.get("system")
                display = coding.get("display")

                # Résoudre le code MOS si display n'est pas fourni
                if not display and code and system:
                    resolver = get_mos_resolver()
                    display = resolver.resolve(system, code)

                return {"system": system, "code": code, "display": display}
        return None

    # Propriétaire
    @property
    def owner_id(self) -> Optional[str]:
        """ID de l'organisation propriétaire."""
        owner = self._data.get("owner", {})
        ref = owner.get("reference")
        return ref.split("/")[-1] if ref else None

    # Autorisation
    @property
    def authorization(self) -> Optional[AuthorizationHelper]:
        """Autorisation du device."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if "authorization" in ext.get("url", "").lower():
                return AuthorizationHelper(ext)
        return None

    @property
    def raw(self) -> Dict[str, Any]:
        """Données brutes JSON."""
        return self._data

    def __repr__(self) -> str:
        return f"<Device {self.id} - {self.manufacturer}>"


def wrap_healthcare_service(data: Dict[str, Any]) -> HealthcareServiceHelper:
    """Enveloppe un HealthcareService dans un helper."""
    return HealthcareServiceHelper(data)


def wrap_device(data: Dict[str, Any]) -> DeviceHelper:
    """Enveloppe un Device dans un helper."""
    return DeviceHelper(data)
