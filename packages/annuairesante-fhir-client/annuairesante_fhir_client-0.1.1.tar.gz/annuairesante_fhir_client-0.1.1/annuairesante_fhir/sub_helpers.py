"""Helpers pour les sous-éléments des ressources FHIR."""

from datetime import date
from typing import Any, Dict, List, Optional

from annuairesante_fhir.mos_resolver import get_resolver


class QualificationHelper:
    """Helper pour accéder aux données d'une qualification."""

    def __init__(self, data: Dict[str, Any], resolve_mos: bool = True):
        """
        Args:
            data: Dictionnaire JSON de la qualification
            resolve_mos: Si True, résout les codes MOS automatiquement
        """
        self._data = data
        self._resolve_mos = resolve_mos
        self._resolver = get_resolver() if resolve_mos else None

    @property
    def codes(self) -> List[Dict[str, Any]]:
        """Liste des codes de la qualification avec résolution MOS.

        Returns:
            Liste de dictionnaires avec 'code', 'system', 'display'
        """
        result = []
        code_obj = self._data.get("code", {})
        codings = code_obj.get("coding", [])

        for coding in codings:
            code = coding.get("code")
            system = coding.get("system")
            display = coding.get("display")

            # Résoudre avec MOS si display n'est pas fourni et résolution activée
            if not display and self._resolve_mos and self._resolver and system and code:
                display = self._resolver.resolve(system, code)

            result.append({"system": system, "code": code, "display": display})

        return result

    @property
    def type_diplome(self) -> Optional[str]:
        """Code du type de diplôme (ex: 'DE')."""
        for code in self.codes:
            if "TRE_R14-TypeDiplome" in (code.get("system") or ""):
                return code.get("code")
        return None

    @property
    def type_diplome_display(self) -> Optional[str]:
        """Libellé du type de diplôme."""
        for code in self.codes:
            if "TRE_R14-TypeDiplome" in (code.get("system") or ""):
                return code.get("resolved_display") or code.get("display")
        return None

    @property
    def diplome(self) -> Optional[str]:
        """Code du diplôme (ex: 'DE09')."""
        for code in self.codes:
            if "TRE_R48-DiplomeEtatFrancais" in (code.get("system") or ""):
                return code.get("code")
        return None

    @property
    def diplome_display(self) -> Optional[str]:
        """Libellé du diplôme."""
        for code in self.codes:
            if "TRE_R48-DiplomeEtatFrancais" in (code.get("system") or ""):
                return code.get("resolved_display") or code.get("display")
        return None

    @property
    def categorie_professionnelle(self) -> Optional[str]:
        """Code de la catégorie professionnelle (ex: 'C' pour Civil)."""
        for code in self.codes:
            if "TRE_R09-CategorieProfessionnelle" in (code.get("system") or ""):
                return code.get("code")
        return None

    @property
    def categorie_professionnelle_display(self) -> Optional[str]:
        """Libellé de la catégorie professionnelle."""
        for code in self.codes:
            if "TRE_R09-CategorieProfessionnelle" in (code.get("system") or ""):
                return code.get("resolved_display") or code.get("display")
        return None

    @property
    def profession(self) -> Optional[str]:
        """Code de la profession (ex: '60' pour Infirmier)."""
        for code in self.codes:
            if "TRE_G15-ProfessionSante" in (code.get("system") or ""):
                return code.get("code")
        return None

    @property
    def profession_display(self) -> Optional[str]:
        """Libellé de la profession."""
        for code in self.codes:
            if "TRE_G15-ProfessionSante" in (code.get("system") or ""):
                return code.get("resolved_display") or code.get("display")
        return None

    @property
    def type(self) -> str:
        """Type de qualification (diplome ou profession)."""
        if self.diplome or self.type_diplome:
            return "diplome"
        elif self.profession or self.categorie_professionnelle:
            return "profession"
        return "unknown"

    @property
    def summary(self) -> str:
        """Résumé de la qualification."""
        if self.type == "diplome":
            parts = []
            if self.type_diplome_display:
                parts.append(self.type_diplome_display)
            if self.diplome_display:
                parts.append(self.diplome_display)
            return " - ".join(parts) if parts else f"Diplôme {self.diplome or self.type_diplome}"
        elif self.type == "profession":
            parts = []
            if self.categorie_professionnelle_display:
                parts.append(self.categorie_professionnelle_display)
            if self.profession_display:
                parts.append(self.profession_display)
            return " - ".join(parts) if parts else f"Profession {self.profession}"
        return "Qualification inconnue"

    @property
    def period_start(self) -> Optional[date]:
        """Date de début de validité."""
        period = self._data.get("period", {})
        start = period.get("start")
        if start:
            try:
                return date.fromisoformat(start.split("T")[0])
            except Exception:
                pass
        return None

    @property
    def period_end(self) -> Optional[date]:
        """Date de fin de validité."""
        period = self._data.get("period", {})
        end = period.get("end")
        if end:
            try:
                return date.fromisoformat(end.split("T")[0])
            except Exception:
                pass
        return None

    @property
    def issuer(self) -> Optional[str]:
        """Émetteur de la qualification."""
        issuer = self._data.get("issuer", {})
        return issuer.get("display") or issuer.get("reference")

    def __repr__(self) -> str:
        return f"<Qualification {self.type}: {self.summary}>"


class IdentifierHelper:
    """Helper pour accéder aux données d'un identifiant."""

    def __init__(self, data: Dict[str, Any], resolve_mos: bool = True):
        """
        Args:
            data: Dictionnaire JSON de l'identifiant
            resolve_mos: Si True, résout les codes MOS automatiquement
        """
        self._data = data
        self._resolve_mos = resolve_mos
        self._resolver = get_resolver() if resolve_mos else None

    @property
    def value(self) -> Optional[str]:
        """Valeur de l'identifiant."""
        return self._data.get("value")

    @property
    def system(self) -> Optional[str]:
        """Système de l'identifiant."""
        return self._data.get("system")

    @property
    def type_code(self) -> Optional[str]:
        """Code du type d'identifiant (ex: 'RPPS', 'ADELI', 'IDNPS')."""
        type_obj = self._data.get("type", {})
        codings = type_obj.get("coding", [])
        if codings:
            return codings[0].get("code")
        return None

    @property
    def type_display(self) -> Optional[str]:
        """Libellé du type d'identifiant."""
        type_obj = self._data.get("type", {})
        codings = type_obj.get("coding", [])
        if codings:
            coding = codings[0]

            # Essayer d'abord le display existant
            display = coding.get("display")
            if display:
                return display

            # Sinon résoudre avec MOS
            if self._resolve_mos and self._resolver:
                system = coding.get("system")
                code = coding.get("code")
                if system and code:
                    resolved = self._resolver.resolve(system, code)
                    if resolved:
                        return resolved

            # Fallback sur le code
            return coding.get("code")
        return None

    @property
    def use(self) -> Optional[str]:
        """Usage de l'identifiant (ex: 'official')."""
        return self._data.get("use")

    @property
    def is_rpps(self) -> bool:
        """Vérifie si c'est un identifiant RPPS."""
        return self.type_code == "RPPS" or "rpps" in (self.system or "").lower()

    @property
    def is_adeli(self) -> bool:
        """Vérifie si c'est un identifiant ADELI."""
        return self.type_code == "ADELI" or "adeli" in (self.system or "").lower()

    @property
    def is_idnps(self) -> bool:
        """Vérifie si c'est un identifiant IDNPS."""
        return self.type_code == "IDNPS"

    @property
    def is_finess(self) -> bool:
        """Vérifie si c'est un identifiant FINESS."""
        return (
            self.type_code == "FINESS"
            or self.type_code == "FINEJ"
            or self.type_code == "FINEG"
            or "finess" in (self.system or "").lower()
        )

    @property
    def is_fineg(self) -> bool:
        """Vérifie si c'est un identifiant FINEG (FINESS géographique)."""
        return self.type_code == "FINEG"

    @property
    def is_finej(self) -> bool:
        """Vérifie si c'est un identifiant FINEJ (FINESS juridique)."""
        return self.type_code == "FINEJ"

    @property
    def is_idnst(self) -> bool:
        """Vérifie si c'est un identifiant IDNST (Identifiant National de Structure)."""
        return self.type_code == "IDNST"

    @property
    def is_siret(self) -> bool:
        """Vérifie si c'est un identifiant SIRET."""
        return self.type_code == "SIRET" or "siret" in (self.system or "").lower()

    def __repr__(self) -> str:
        type_str = self.type_display or self.type_code or "Unknown"
        return f"<Identifier {type_str}={self.value}>"


class TelecomHelper:
    """Helper pour accéder aux données d'un moyen de contact."""

    def __init__(self, data: Dict[str, Any]):
        """
        Args:
            data: Dictionnaire JSON du telecom
        """
        self._data = data

    @property
    def system(self) -> Optional[str]:
        """Système de contact (email, phone, fax, etc.)."""
        return self._data.get("system")

    @property
    def value(self) -> Optional[str]:
        """Valeur du contact."""
        return self._data.get("value")

    @property
    def use(self) -> Optional[str]:
        """Usage du contact (work, home, mobile, etc.)."""
        return self._data.get("use")

    @property
    def rank(self) -> Optional[int]:
        """Rang de préférence du contact."""
        return self._data.get("rank")

    @property
    def is_email(self) -> bool:
        """Vérifie si c'est un email."""
        return self.system == "email"

    @property
    def is_phone(self) -> bool:
        """Vérifie si c'est un téléphone."""
        return self.system == "phone"

    @property
    def is_mssante(self) -> bool:
        """Vérifie si c'est une messagerie MSSanté."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if "email-type" in ext.get("url", ""):
                coding = ext.get("valueCoding", {})
                if coding.get("code") == "MSSANTE":
                    return True
        return False

    @property
    def mssante_type(self) -> Optional[str]:
        """Type de BAL MSSanté (PER, ORG, APP, etc.)."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if "mailbox-mss-metadata" in ext.get("url", ""):
                sub_extensions = ext.get("extension", [])
                for sub_ext in sub_extensions:
                    if sub_ext.get("url") == "type":
                        codings = sub_ext.get("valueCodeableConcept", {}).get("coding", [])
                        if codings:
                            return codings[0].get("code")
        return None

    @property
    def mssante_description(self) -> Optional[str]:
        """Description de la BAL MSSanté."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if "mailbox-mss-metadata" in ext.get("url", ""):
                sub_extensions = ext.get("extension", [])
                for sub_ext in sub_extensions:
                    if sub_ext.get("url") == "description":
                        return sub_ext.get("valueString")
        return None

    @property
    def mssante_service(self) -> Optional[str]:
        """Service associé à la BAL MSSanté."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if "mailbox-mss-metadata" in ext.get("url", ""):
                sub_extensions = ext.get("extension", [])
                for sub_ext in sub_extensions:
                    if sub_ext.get("url") == "service":
                        return sub_ext.get("valueString")
        return None

    @property
    def mssante_digitization(self) -> Optional[bool]:
        """Indique si la BAL MSSanté a la numérisation activée."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if "mailbox-mss-metadata" in ext.get("url", ""):
                sub_extensions = ext.get("extension", [])
                for sub_ext in sub_extensions:
                    if sub_ext.get("url") == "digitization":
                        return sub_ext.get("valueBoolean")
        return None

    def __repr__(self) -> str:
        return f"<Telecom {self.system}={self.value}>"


class SmartcardHelper:
    """Helper pour accéder aux données d'une carte professionnelle."""

    def __init__(self, data: Dict[str, Any]):
        """
        Args:
            data: Dictionnaire JSON de l'extension smartcard
        """
        self._data = data

    @property
    def type_code(self) -> Optional[str]:
        """Code du type de carte (ex: 'CPS')."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if ext.get("url") == "type":
                codings = ext.get("valueCodeableConcept", {}).get("coding", [])
                if codings:
                    return codings[0].get("code")
        return None

    @property
    def number(self) -> Optional[str]:
        """Numéro de la carte."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if ext.get("url") == "number":
                return ext.get("valueString")
        return None

    @property
    def period_start(self) -> Optional[date]:
        """Date de début de validité."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if ext.get("url") == "period":
                period = ext.get("valuePeriod", {})
                start = period.get("start")
                if start:
                    try:
                        return date.fromisoformat(start.split("T")[0])
                    except Exception:
                        pass
        return None

    @property
    def period_end(self) -> Optional[date]:
        """Date de fin de validité."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if ext.get("url") == "period":
                period = ext.get("valuePeriod", {})
                end = period.get("end")
                if end:
                    try:
                        return date.fromisoformat(end.split("T")[0])
                    except Exception:
                        pass
        return None

    @property
    def is_valid(self) -> bool:
        """Vérifie si la carte est actuellement valide."""
        today = date.today()
        start = self.period_start
        end = self.period_end

        if start and today < start:
            return False
        if end and today > end:
            return False

        return True

    def __repr__(self) -> str:
        return f"<Smartcard {self.type_code}={self.number}>"


class NameHelper:
    """Helper pour accéder aux données d'un nom."""

    def __init__(self, data: Dict[str, Any]):
        """
        Args:
            data: Dictionnaire JSON du name
        """
        self._data = data

    @property
    def text(self) -> Optional[str]:
        """Texte complet du nom."""
        return self._data.get("text")

    @property
    def family(self) -> Optional[str]:
        """Nom de famille."""
        return self._data.get("family")

    @property
    def given(self) -> List[str]:
        """Prénoms."""
        return self._data.get("given", [])

    @property
    def prefix(self) -> List[str]:
        """Préfixes (civilité)."""
        return self._data.get("prefix", [])

    @property
    def suffix(self) -> List[str]:
        """Suffixes."""
        return self._data.get("suffix", [])

    @property
    def use(self) -> Optional[str]:
        """Usage du nom (official, usual, etc.)."""
        return self._data.get("use")

    @property
    def full_name(self) -> str:
        """Construit le nom complet."""
        parts = []

        if self.prefix:
            parts.extend(self.prefix)
        if self.given:
            parts.extend(self.given)
        if self.family:
            parts.append(self.family)
        if self.suffix:
            parts.extend(self.suffix)

        return " ".join(parts) if parts else self.text or ""

    def __repr__(self) -> str:
        return f"<Name {self.full_name}>"


class AddressHelper:
    """Helper pour accéder aux données d'une adresse."""

    def __init__(self, data: Dict[str, Any]):
        """
        Args:
            data: Dictionnaire JSON de l'address
        """
        self._data = data

    @property
    def use(self) -> Optional[str]:
        """Usage de l'adresse (home, work, etc.)."""
        return self._data.get("use")

    @property
    def type(self) -> Optional[str]:
        """Type d'adresse (postal, physical, both)."""
        return self._data.get("type")

    @property
    def text(self) -> Optional[str]:
        """Texte complet de l'adresse."""
        return self._data.get("text")

    @property
    def line(self) -> List[str]:
        """Lignes d'adresse."""
        lines = self._data.get("line", [])
        return [line for line in lines if line is not None]

    @property
    def city(self) -> Optional[str]:
        """Ville."""
        return self._data.get("city")

    @property
    def district(self) -> Optional[str]:
        """District/Département."""
        return self._data.get("district")

    @property
    def postal_code(self) -> Optional[str]:
        """Code postal."""
        return self._data.get("postalCode")

    @property
    def country(self) -> Optional[str]:
        """Pays."""
        return self._data.get("country")

    @property
    def insee_code(self) -> Optional[str]:
        """Code INSEE de la commune."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if "insee-code" in ext.get("url", ""):
                coding = ext.get("valueCoding", {})
                return coding.get("code")
        return None

    @property
    def street_name_type(self) -> Optional[str]:
        """Type de voie (RUE, AVE, etc.)."""
        line_extensions = self._data.get("_line", [])
        for line_ext in line_extensions:
            if line_ext:
                extensions = line_ext.get("extension", [])
                for ext in extensions:
                    if "streetNameType" in ext.get("url", ""):
                        return ext.get("valueString")
        return None

    @property
    def street_name_base(self) -> Optional[str]:
        """Nom de base de la voie."""
        line_extensions = self._data.get("_line", [])
        for line_ext in line_extensions:
            if line_ext:
                extensions = line_ext.get("extension", [])
                for ext in extensions:
                    if "streetNameBase" in ext.get("url", ""):
                        return ext.get("valueString")
        return None

    @property
    def lieu_dit(self) -> Optional[str]:
        """Lieu-dit."""
        line_extensions = self._data.get("_line", [])
        for line_ext in line_extensions:
            if line_ext:
                extensions = line_ext.get("extension", [])
                for ext in extensions:
                    if "lieu-dit" in ext.get("url", ""):
                        return ext.get("valueString")
        return None

    @property
    def full_address(self) -> str:
        """Construit l'adresse complète."""
        parts = []

        if self.line:
            parts.extend(self.line)

        if self.lieu_dit:
            parts.append(self.lieu_dit)

        city_line = []
        if self.postal_code:
            city_line.append(self.postal_code)
        if self.city:
            city_line.append(self.city)

        if city_line:
            parts.append(" ".join(city_line))

        if self.country:
            parts.append(self.country)

        return "\n".join(parts) if parts else self.text or ""

    def __repr__(self) -> str:
        return f"<Address {self.city} {self.postal_code}>"


class AuthorizationHelper:
    """Helper pour accéder aux données d'une autorisation (extension as-ext-authorization)."""

    def __init__(self, data: Dict[str, Any]):
        """
        Args:
            data: Dictionnaire JSON de l'extension d'autorisation
        """
        self._data = data

    @property
    def date_authorization(self) -> Optional[str]:
        """Date d'autorisation."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if ext.get("url") == "dateAuthorization":
                return ext.get("valueDate")
        return None

    @property
    def period_start(self) -> Optional[str]:
        """Date de début de la période d'autorisation."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if ext.get("url") == "periodAuthorization":
                period = ext.get("valuePeriod", {})
                return period.get("start")
        return None

    @property
    def period_end(self) -> Optional[str]:
        """Date de fin de la période d'autorisation."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if ext.get("url") == "periodAuthorization":
                period = ext.get("valuePeriod", {})
                return period.get("end")
        return None

    @property
    def deleted(self) -> Optional[bool]:
        """Autorisation supprimée."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            if ext.get("url") == "deletedAuthorization":
                return ext.get("valueBoolean")
        return None

    @property
    def is_active(self) -> bool:
        """Vérifie si l'autorisation est active (non supprimée et dans la période)."""
        if self.deleted:
            return False

        # Vérifier si on est dans la période
        if self.period_start or self.period_end:
            from datetime import date

            today = date.today()

            if self.period_start:
                start = date.fromisoformat(self.period_start)
                if today < start:
                    return False

            if self.period_end:
                end = date.fromisoformat(self.period_end)
                if today > end:
                    return False

        return True

    def __repr__(self) -> str:
        return f"<Authorization {self.date_authorization} - {self.period_start}/{self.period_end}>"
