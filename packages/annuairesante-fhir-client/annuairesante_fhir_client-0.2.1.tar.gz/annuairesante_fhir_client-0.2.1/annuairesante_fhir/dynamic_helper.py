"""Helper dynamique qui s'adapte automatiquement à la structure FHIR."""

from typing import Any, Dict, List, Optional, Union

from annuairesante_fhir.mos_resolver import get_resolver


class FHIRResource:
    """
    Wrapper dynamique bas niveau pour ressources FHIR.

    Permet un accès dynamique aux données FHIR avec notation pointée et résolution MOS automatique.
    Pour des méthodes d'accès simplifiées, utilisez les helpers (PractitionerHelper, etc.).

    Exemple:
        >>> from annuairesante_fhir.dynamic_helper import fhir
        >>> p = fhir(practitioner_data, auto_resolve_mos=True)
        >>> p.name[0].family  # "Dupont"
        >>> p.identifier[0].value  # Accès direct aux données FHIR
        >>> p.raw  # Accès aux données brutes
    """

    def __init__(self, data: Dict[str, Any], auto_resolve_mos: bool = False):
        """
        Args:
            data: Dictionnaire JSON de la ressource FHIR
            auto_resolve_mos: Si True, résout automatiquement les codes MOS
        """
        self._data = data
        self._auto_resolve_mos = auto_resolve_mos
        self._resolver = get_resolver() if auto_resolve_mos else None

        # Cache pour propriétés calculées
        self._cache = {}

    def __getattr__(self, name: str) -> Any:
        """
        Accès dynamique aux attributs FHIR.

        Priorité:
        1. Champs FHIR directs
        2. Extensions si le nom commence par 'ext_'
        """
        # Éviter la récursion infinie
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        # Vérifier le cache
        if name in self._cache:
            return self._cache[name]

        # 1. Champs FHIR directs
        if name in self._data:
            value = self._wrap_value(self._data[name])
            self._cache[name] = value
            return value

        # 2. Extensions (ex: ext_smartcard)
        if name.startswith("ext_"):
            ext_name = name[4:]  # Enlever 'ext_'
            ext_value = self._get_extension(ext_name)
            if ext_value is not None:
                self._cache[name] = ext_value
                return ext_value

        # Pas trouvé
        return None

    def __getitem__(self, key: Union[str, int]) -> Any:
        """Support de l'accès par index ou clé."""
        if isinstance(key, int) and isinstance(self._data, list):
            return self._wrap_value(self._data[key])
        return self.__getattr__(key)

    def _wrap_value(self, value: Any) -> Any:
        """Enveloppe récursivement les valeurs."""
        if isinstance(value, dict):
            # Résoudre les codes MOS si demandé
            if self._auto_resolve_mos and "coding" in value:
                return self._resolve_codeable_concept(value)
            return FHIRResource(value, self._auto_resolve_mos)
        elif isinstance(value, list):
            return FHIRList([self._wrap_value(item) for item in value])
        return value

    def _resolve_codeable_concept(self, codeable: Dict) -> Any:
        """Résout un CodeableConcept avec MOS."""
        codings = codeable.get("coding", [])
        if not codings:
            return FHIRResource(codeable, self._auto_resolve_mos)

        # Créer une version enrichie
        enriched = codeable.copy()
        enriched_codings = []

        for coding in codings:
            enriched_coding = coding.copy()
            if self._resolver:
                resolved = self._resolver.resolve_coding(coding)
                if resolved and resolved != coding.get("code"):
                    enriched_coding["resolved_display"] = resolved
            enriched_codings.append(enriched_coding)

        enriched["coding"] = enriched_codings
        return FHIRResource(enriched, self._auto_resolve_mos)

    def _get_extension(self, ext_name: str) -> Optional[Any]:
        """Récupère une extension par nom."""
        extensions = self._data.get("extension", [])
        for ext in extensions:
            url = ext.get("url", "")
            if ext_name in url or url.endswith(ext_name):
                # Parser l'extension de manière intelligente
                return self._parse_extension(ext)
        return None

    def _parse_extension(self, ext: Dict) -> Any:
        """Parse une extension FHIR."""
        # Si c'est une extension composite (avec sous-extensions)
        if "extension" in ext:
            result = {}
            for sub_ext in ext["extension"]:
                url = sub_ext.get("url", "")
                key = url.split("/")[-1] if "/" in url else url

                # Trouver la valeur (value[Type])
                for k, v in sub_ext.items():
                    if k.startswith("value"):
                        result[key] = v
                        break

            return result

        # Extension simple
        for k, v in ext.items():
            if k.startswith("value"):
                return v

        return ext

    @property
    def raw(self) -> Dict[str, Any]:
        """Accès aux données brutes."""
        return self._data

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return self._data

    def __repr__(self) -> str:
        resource_type = self._data.get("resourceType", "Unknown")
        resource_id = self._data.get("id", "no-id")
        return f"<FHIRResource {resource_type}/{resource_id}>"

    def __str__(self) -> str:
        resource_type = self._data.get("resourceType", "Unknown")
        resource_id = self._data.get("id", "unknown")
        return f"{resource_type}/{resource_id}"


class FHIRList(list):
    """Liste qui enveloppe automatiquement les éléments."""

    def __getattr__(self, name: str) -> List[Any]:
        """
        Permet d'appeler une propriété sur tous les éléments.

        Exemple:
            >>> names = p.name
            >>> names.family  # Retourne [name.family for name in names]
        """
        return [getattr(item, name) if hasattr(item, name) else None for item in self]

    def first(self) -> Any:
        """Retourne le premier élément ou None."""
        return self[0] if self else None

    def last(self) -> Any:
        """Retourne le dernier élément ou None."""
        return self[-1] if self else None


def fhir(data: Dict[str, Any], auto_resolve_mos: bool = False) -> FHIRResource:
    """
    Crée un wrapper FHIR dynamique bas niveau.

    Args:
        data: Dictionnaire JSON de la ressource FHIR
        auto_resolve_mos: Si True, résout automatiquement les codes MOS

    Returns:
        FHIRResource avec accès dynamique aux données FHIR

    Example:
        >>> from annuairesante_fhir import AnnuaireSanteClient
        >>> from annuairesante_fhir.dynamic_helper import fhir
        >>>
        >>> client = AnnuaireSanteClient()
        >>> result = client.practitioner.search(family="Dupont")
        >>> p = fhir(result.entries[0], auto_resolve_mos=True)
        >>>
        >>> # Accès FHIR direct
        >>> print(p.name[0].family)
        >>> print(p.identifier[0].value)
        >>> print(p.qualification[0].code.coding[0].resolved_display)
        >>>
        >>> # Pour des méthodes simplifiées, utilisez les helpers:
        >>> from annuairesante_fhir.helpers import wrap_practitioner
        >>> helper = wrap_practitioner(result.entries[0])
        >>> print(helper.name)  # Nom complet
        >>> print(helper.rpps)  # RPPS extrait
    """
    return FHIRResource(data, auto_resolve_mos)
