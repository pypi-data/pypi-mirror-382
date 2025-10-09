"""Résolveur de codes MOS (Modèle des Objets de Santé)."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class MOSResolver:
    """
    Résolveur de codes MOS pour obtenir les libellés.

    Les codes MOS sont référencés sur https://mos.esante.gouv.fr/NOS/

    Utilise exclusivement les données téléchargées via mos_downloader.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Args:
            cache_dir: Répertoire de cache (défaut: $ANNUAIRE_SANTE_CACHE_DIR ou ~/.annuairesante_cache/)
        """
        if cache_dir is None:
            # Vérifier la variable d'environnement
            env_cache = os.getenv("ANNUAIRE_SANTE_CACHE_DIR")
            if env_cache:
                cache_dir = env_cache
            else:
                cache_dir = os.path.join(Path.home(), ".annuairesante_cache")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Dict[str, str]] = {}

        # Index téléchargé depuis MOS
        self._mos_index: Optional[Dict[str, Dict[str, str]]] = None
        self._auto_init_attempted = False  # Flag pour éviter les boucles infinies
        self._load_mos_index()

        # Charger le cache existant
        self._load_cache()

    def _load_mos_index(self):
        """Charge l'index MOS téléchargé."""
        mos_dir = self.cache_dir / "mos"
        index_file = mos_dir / "lookup_index.json"

        if index_file.exists():
            try:
                with open(index_file, encoding="utf-8") as f:
                    self._mos_index = json.load(f)
                logger.info("Index MOS chargé: %d tables", len(self._mos_index))
            except Exception as e:
                logger.warning("Erreur chargement index MOS: %s", e)
                self._mos_index = None
        else:
            # Vérifier si auto-init est activé et n'a pas déjà été tenté
            auto_init_value = os.getenv("ANNUAIRE_SANTE_AUTO_INIT_MOS", "false")

            if auto_init_value.lower() in ("true", "1", "yes") and not self._auto_init_attempted:
                self._auto_init_attempted = True  # Marquer comme tenté avant d'appeler
                logger.info("Initialisation automatique du cache MOS activée...")
                self._auto_init_cache()
            elif not self._auto_init_attempted:
                logger.warning("Index MOS non trouvé: %s", index_file)
                logger.info(
                    "Téléchargez les référentiels avec: python examples/download_mos.py essential"
                )
                logger.info(
                    "Ou activez l'initialisation automatique avec ANNUAIRE_SANTE_AUTO_INIT_MOS=true"
                )
                self._mos_index = None
            else:
                # Auto-init déjà tenté mais a échoué
                logger.warning("Index MOS non disponible après initialisation automatique")
                self._mos_index = None

    def _auto_init_cache(self):
        """Initialise automatiquement le cache MOS avec les référentiels essentiels."""
        try:
            # Import ici pour éviter les imports circulaires
            from .mos_downloader import MOSDownloader

            logger.info("Téléchargement des référentiels MOS essentiels...")

            downloader = MOSDownloader(cache_dir=str(self.cache_dir / "mos"))

            # Télécharger uniquement les TRE essentiels (rapide)
            stats = downloader.download_all(
                force=False,
                include_patterns=["TRE_R*"]  # Seulement les TRE (tables de référence)
            )

            logger.info("Téléchargement terminé: %d référentiels téléchargés", stats.get("downloaded", 0))

            # Construire l'index de recherche si des fichiers ont été téléchargés
            if stats.get("downloaded", 0) > 0 or stats.get("skipped", 0) > 0:
                logger.info("Construction de l'index de recherche...")
                downloader.build_lookup_index()

            # Recharger l'index (éviter la récursion en chargeant directement)
            mos_dir = self.cache_dir / "mos"
            index_file = mos_dir / "lookup_index.json"
            if index_file.exists():
                with open(index_file, encoding="utf-8") as f:
                    self._mos_index = json.load(f)
                logger.info("Index MOS rechargé: %d tables", len(self._mos_index))
            else:
                logger.warning("Index MOS non trouvé après téléchargement")
                self._mos_index = None

        except Exception as e:
            logger.error("Erreur lors de l'initialisation automatique du cache MOS: %s", e)
            self._mos_index = None


    def _load_cache(self):
        """Charge le cache depuis le disque."""
        cache_file = self.cache_dir / "mos_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                pass

    def _save_cache(self):
        """Sauvegarde le cache sur le disque."""
        cache_file = self.cache_dir / "mos_cache.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def resolve(self, system: str, code: str) -> Optional[str]:
        """
        Résout un code MOS pour obtenir son libellé.

        Args:
            system: URL du système (ex: "https://mos.esante.gouv.fr/NOS/TRE_R48-DiplomeEtatFrancais/...")
            code: Code à résoudre (ex: "DE28")

        Returns:
            Libellé du code ou None si non trouvé

        Example:
            >>> resolver = MOSResolver()
            >>> resolver.resolve(
            ...     "https://mos.esante.gouv.fr/NOS/TRE_R48-DiplomeEtatFrancais/FHIR/TRE-R48-DiplomeEtatFrancais",
            ...     "DE28"
            ... )
            "Diplôme d'État de docteur en médecine"
        """
        # Vérifier le cache
        cache_key = f"{system}#{code}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Extraire le nom de la table de référence du système
        table = self._extract_table_name(system)
        if not table:
            return None

        # Utiliser l'index MOS téléchargé
        if self._mos_index and table in self._mos_index:
            display = self._mos_index[table].get(code)
            if display:
                self._cache[cache_key] = display
                self._save_cache()
                return display

        # Aucune résolution possible
        return None

    def _extract_table_name(self, system: str) -> Optional[str]:
        """Extrait le nom de table de référence depuis l'URL du système."""
        if "/TRE" in system:
            # Ex: ".../TRE_R48-DiplomeEtatFrancais/..." -> "TRE-R48"
            # Ex: ".../TRE-R48-DiplomeEtatFrancais/..." -> "TRE-R48"
            parts = system.split("/TRE")
            if len(parts) > 1:
                # Prendre tout jusqu'au prochain /
                table_part = "TRE" + parts[1].split("/")[0]

                # Extraire juste TRE_RXX ou TRE-RXX
                # Format possible: TRE_R48-DiplomeEtatFrancais ou TRE-R48-DiplomeEtatFrancais

                # Séparer par - pour enlever le nom de la table
                if "-" in table_part:
                    # "TRE_R48-DiplomeEtat..." -> ["TRE_R48", "DiplomeEtat..."]
                    code_part = table_part.split("-")[0]
                    # Normaliser avec tirets : TRE_R48 ou TRE-R48 -> TRE-R48
                    return code_part.replace("_", "-")
                else:
                    # Cas où il n'y a pas de - (rare)
                    return table_part.replace("_", "-")

        # Support pour JDV et ASS
        if "/JDV" in system:
            parts = system.split("/JDV")
            if len(parts) > 1:
                table_part = "JDV" + parts[1].split("/")[0]
                if "-" in table_part:
                    code_part = table_part.split("-")[0]
                    return code_part.replace("_", "-")
                return table_part.replace("_", "-")

        if "/ASS" in system:
            parts = system.split("/ASS")
            if len(parts) > 1:
                table_part = "ASS" + parts[1].split("/")[0]
                if "-" in table_part:
                    code_part = table_part.split("-")[0]
                    return code_part.replace("_", "-")
                return table_part.replace("_", "-")

        return None

    def reload_index(self):
        """Recharge l'index MOS depuis le disque."""
        self._load_mos_index()
        logger.info("Index MOS rechargé")

    def resolve_coding(self, coding: Dict) -> str:
        """
        Résout un objet coding FHIR.

        Args:
            coding: Dictionnaire contenant system, code, display

        Returns:
            Libellé (display si présent, sinon résolu, sinon code)
        """
        # Si display est déjà présent, le retourner
        if coding.get("display"):
            return coding["display"]

        # Sinon, essayer de résoudre
        system = coding.get("system")
        code = coding.get("code")

        if system and code:
            resolved = self.resolve(system, code)
            if resolved:
                return resolved

        # Fallback sur le code
        return code or "Unknown"

    def enrich_qualifications(self, qualifications: list) -> list:
        """
        Enrichit une liste de qualifications avec les libellés MOS.

        Args:
            qualifications: Liste de qualifications (depuis PractitionerHelper)

        Returns:
            Liste enrichie avec les libellés
        """
        result = []
        for qual in qualifications:
            enriched_codes = []

            for code_info in qual.get("codes", []):
                display = self.resolve_coding(code_info)
                enriched_codes.append({**code_info, "resolved_display": display})

            result.append({**qual, "codes": enriched_codes})

        return result

    def get_stats(self) -> Dict:
        """Retourne les statistiques de l'index MOS."""
        if not self._mos_index:
            return {
                "loaded": False,
                "tables_count": 0,
                "total_codes": 0,
                "cache_hits": len(self._cache),
            }

        total_codes = sum(len(codes) for codes in self._mos_index.values())

        return {
            "loaded": True,
            "tables_count": len(self._mos_index),
            "total_codes": total_codes,
            "cache_hits": len(self._cache),
        }


# Instance globale singleton
_resolver = None


def get_resolver() -> MOSResolver:
    """Retourne l'instance singleton du résolveur MOS."""
    global _resolver
    if _resolver is None:
        _resolver = MOSResolver()
    return _resolver


def resolve_code(system: str, code: str) -> Optional[str]:
    """
    Fonction helper pour résoudre un code MOS.

    Args:
        system: URL du système MOS
        code: Code à résoudre

    Returns:
        Libellé ou None
    """
    return get_resolver().resolve(system, code)
