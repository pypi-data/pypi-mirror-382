"""Téléchargeur et gestionnaire de référentiels MOS/NOS depuis esante.gouv.fr."""

import json
import os
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup


class MOSDownloader:
    """
    Téléchargeur de référentiels MOS/NOS depuis https://mos.esante.gouv.fr/NOS/

    Gère le téléchargement incrémental basé sur les dates de modification.
    """

    BASE_URL = "https://mos.esante.gouv.fr/NOS/"

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Args:
            cache_dir: Répertoire de cache (défaut: $ANNUAIRE_SANTE_CACHE_DIR/mos ou ~/.annuairesante_cache/mos/)
        """
        if cache_dir is None:
            # Vérifier la variable d'environnement
            env_cache = os.getenv("ANNUAIRE_SANTE_CACHE_DIR")
            if env_cache:
                cache_dir = Path(env_cache) / "mos"
            else:
                cache_dir = Path.home() / ".annuairesante_cache" / "mos"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Fichier de métadonnées pour tracker les dates de mise à jour
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()

        # Statistiques de téléchargement
        self.stats = {"downloaded": 0, "skipped": 0, "errors": 0, "total": 0}

    def _load_metadata(self) -> Dict:
        """Charge les métadonnées de téléchargement."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_full_sync": None, "terminologies": {}}

    def _save_metadata(self):
        """Sauvegarde les métadonnées."""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Erreur sauvegarde métadonnées: {e}")

    def list_terminologies(self, force_refresh: bool = False) -> List[Dict[str, str]]:
        """
        Liste tous les référentiels disponibles (TRE_*, JDV_*, ASS_*).

        Args:
            force_refresh: Force le rafraîchissement de la liste

        Returns:
            Liste de dicts avec 'name', 'url', 'last_modified'
        """
        print("📋 Récupération de la liste des référentiels...")

        try:
            response = httpx.get(self.BASE_URL, timeout=30.0, follow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            terminologies = []

            for link in soup.find_all("a"):
                href = link.get("href", "")

                # Filtrer les référentiels TRE, JDV et ASS
                if any(href.startswith(prefix) for prefix in ["TRE_", "JDV_", "ASS_"]):
                    name = href.rstrip("/")
                    url = urljoin(self.BASE_URL, href)

                    # Extraire la date de modification si disponible
                    parent = link.parent
                    last_modified = None
                    if parent and parent.find_next_sibling():
                        date_text = parent.find_next_sibling().get_text(strip=True)
                        last_modified = self._parse_date(date_text)

                    terminologies.append({"name": name, "url": url, "last_modified": last_modified})

            print(f"✅ {len(terminologies)} référentiels trouvés")
            return terminologies

        except Exception as e:
            print(f"❌ Erreur lors de la récupération de la liste: {e}")
            return []

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse une date du format Apache directory listing."""
        try:
            # Format: "2024-01-15 10:30"
            dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M")
            return dt.isoformat()
        except Exception:
            return None

    def download_terminology(self, name: str, force: bool = False) -> bool:
        """
        Télécharge un référentiel spécifique.

        Args:
            name: Nom du référentiel (ex: "TRE_R48-DiplomeEtatFrancais")
            force: Force le téléchargement même si déjà à jour

        Returns:
            True si téléchargé, False si skippé ou erreur
        """
        # Construire l'URL du fichier JSON FHIR
        # Pattern: /NOS/{name}/FHIR/{normalized-name}/{name}-FHIR.json
        # Ex: TRE_R48-DiplomeEtatFrancais → TRE-R48-DiplomeEtatFrancais
        normalized_name = name.replace("_", "-")

        base_url = urljoin(self.BASE_URL, f"{name}/FHIR/{normalized_name}/")
        json_url = urljoin(base_url, f"{name}-FHIR.json")

        # Vérifier si mise à jour nécessaire
        if not force and name in self.metadata["terminologies"]:
            # Récupérer la date de dernière modification sur le serveur
            try:
                head_response = httpx.head(json_url, timeout=10.0, follow_redirects=True)
                server_last_modified = head_response.headers.get("Last-Modified")

                if server_last_modified:
                    # Parser la date du serveur (format HTTP-date)
                    server_date = parsedate_to_datetime(server_last_modified)

                    # Comparer avec la date de téléchargement local
                    local_date_str = self.metadata["terminologies"][name].get("downloaded_at")
                    if local_date_str:
                        local_date = datetime.fromisoformat(local_date_str)

                        # Si le serveur n'a pas de version plus récente, skip
                        if server_date.replace(tzinfo=None) <= local_date:
                            print(
                                f"⏭️  {name}: à jour (serveur: {server_date.strftime('%Y-%m-%d %H:%M')})"
                            )
                            self.stats["skipped"] += 1
                            return False
                        else:
                            print(
                                f"🔄 {name}: mise à jour disponible (serveur: {server_date.strftime('%Y-%m-%d %H:%M')})"
                            )
                    else:
                        print(f"⏭️  {name}: déjà en cache")
                        self.stats["skipped"] += 1
                        return False
                else:
                    # Pas de Last-Modified header, vérifier juste l'existence
                    print(f"⏭️  {name}: déjà en cache (pas de date serveur)")
                    self.stats["skipped"] += 1
                    return False

            except Exception as e:
                # En cas d'erreur HEAD, continuer avec le téléchargement
                print(f"⚠️  {name}: impossible de vérifier la date ({e}), téléchargement...")

        try:
            # Télécharger le fichier JSON FHIR
            print(f"⬇️  Téléchargement de {name}...")
            response = httpx.get(json_url, timeout=30.0, follow_redirects=True)
            response.raise_for_status()

            # Sauvegarder le fichier
            output_file = self.cache_dir / f"{name}-FHIR.json"
            output_file.write_bytes(response.content)

            # Récupérer la date de modification du serveur
            server_last_modified = response.headers.get("Last-Modified")
            server_date_iso = None
            if server_last_modified:
                try:
                    server_date = parsedate_to_datetime(server_last_modified)
                    server_date_iso = server_date.isoformat()
                except Exception:
                    pass

            # Mettre à jour les métadonnées
            self.metadata["terminologies"][name] = {
                "downloaded_at": datetime.now().isoformat(),
                "server_last_modified": server_date_iso,
                "file": str(output_file),
                "size": len(response.content),
            }
            self._save_metadata()

            print(f"✅ {name}: téléchargé ({len(response.content)} octets)")
            self.stats["downloaded"] += 1
            return True

        except Exception as e:
            print(f"❌ {name}: erreur - {e}")
            self.stats["errors"] += 1
            return False

    def parse_tabs_file(self, terminology_name: str) -> List[Dict[str, str]]:
        """
        Parse un fichier JSON FHIR et retourne les entrées.

        Args:
            terminology_name: Nom du référentiel

        Returns:
            Liste de dicts avec 'code', 'display', etc.
        """
        json_file = self.cache_dir / f"{terminology_name}-FHIR.json"

        if not json_file.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {json_file}")

        entries = []

        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            resource_type = data.get("resourceType")

            # CodeSystem (TRE) : concept[] directement à la racine
            if resource_type == "CodeSystem":
                concepts = data.get("concept", [])
                for concept in concepts:
                    entry = {
                        "code": concept.get("code"),
                        "display": concept.get("display"),
                        "definition": concept.get("definition"),
                        "property": concept.get("property", []),
                    }
                    entries.append(entry)

            # ValueSet (JDV, ASS) : compose.include[].concept[]
            elif resource_type == "ValueSet":
                compose = data.get("compose", {})
                includes = compose.get("include", [])

                for include in includes:
                    concepts = include.get("concept", [])
                    for concept in concepts:
                        entry = {
                            "code": concept.get("code"),
                            "display": concept.get("display"),
                            "designation": concept.get("designation", []),
                        }
                        entries.append(entry)

            return entries

        except Exception as e:
            print(f"❌ Erreur parsing {terminology_name}: {e}")
            return []

    def parse_fhir_json(self, terminology_name: str) -> List[Dict[str, str]]:
        """
        Alias pour parse_tabs_file (pour compatibilité).
        Parse un fichier JSON FHIR.
        """
        return self.parse_tabs_file(terminology_name)

    def download_all(
        self,
        force: bool = False,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, int]:
        """
        Télécharge tous les référentiels.

        Args:
            force: Force le téléchargement même si déjà à jour
            include_patterns: Liste de patterns à inclure (ex: ["TRE_R*", "JDV_J1*"])
            exclude_patterns: Liste de patterns à exclure

        Returns:
            Statistiques de téléchargement
        """
        print("=" * 70)
        print("🚀 TÉLÉCHARGEMENT DES RÉFÉRENTIELS MOS/NOS")
        print("=" * 70)

        # Réinitialiser les stats
        self.stats = {"downloaded": 0, "skipped": 0, "errors": 0, "total": 0}

        # Lister les référentiels
        terminologies = self.list_terminologies()

        # Filtrer selon les patterns
        if include_patterns or exclude_patterns:
            terminologies = self._filter_terminologies(
                terminologies, include_patterns, exclude_patterns
            )

        self.stats["total"] = len(terminologies)

        print(f"\n📦 {len(terminologies)} référentiels à traiter\n")

        # Télécharger chaque référentiel
        for i, term in enumerate(terminologies, 1):
            print(f"[{i}/{len(terminologies)}] ", end="")
            self.download_terminology(term["name"], force=force)

        # Mettre à jour la date de synchronisation complète
        self.metadata["last_full_sync"] = datetime.now().isoformat()
        self._save_metadata()

        # Afficher le résumé
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ")
        print("=" * 70)
        print(f"Total:        {self.stats['total']}")
        print(f"Téléchargés:  {self.stats['downloaded']}")
        print(f"Skippés:      {self.stats['skipped']}")
        print(f"Erreurs:      {self.stats['errors']}")
        print("=" * 70)

        return self.stats

    def _filter_terminologies(
        self,
        terminologies: List[Dict],
        include_patterns: Optional[List[str]],
        exclude_patterns: Optional[List[str]],
    ) -> List[Dict]:
        """Filtre les référentiels selon les patterns."""
        filtered = terminologies

        if include_patterns:
            filtered = [
                t
                for t in filtered
                if any(self._match_pattern(t["name"], p) for p in include_patterns)
            ]

        if exclude_patterns:
            filtered = [
                t
                for t in filtered
                if not any(self._match_pattern(t["name"], p) for p in exclude_patterns)
            ]

        return filtered

    def _match_pattern(self, name: str, pattern: str) -> bool:
        """Vérifie si un nom correspond à un pattern (avec wildcards)."""
        # Convertir le pattern en regex
        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        return bool(re.match(f"^{regex_pattern}$", name))

    def build_lookup_index(self) -> Dict[str, Dict[str, str]]:
        """
        Construit un index de recherche rapide pour tous les référentiels téléchargés.

        Returns:
            Dict[table_name, Dict[code, display]]
        """
        print("🔨 Construction de l'index de recherche...")

        index = {}

        for term_name in self.metadata["terminologies"].keys():
            try:
                entries = self.parse_fhir_json(term_name)

                # Extraire le nom de table normalisé
                table_name = self._extract_table_name(term_name)

                if table_name:
                    index[table_name] = {}

                    for entry in entries:
                        code = entry.get("code")
                        display = entry.get("display")

                        if code and display:
                            index[table_name][code] = display

                    print(f"  ✅ {table_name}: {len(index[table_name])} codes")

            except Exception as e:
                print(f"  ⚠️  {term_name}: {e}")

        # Sauvegarder l'index
        index_file = self.cache_dir / "lookup_index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

        print(f"✅ Index sauvegardé: {index_file}")
        print(f"📊 {len(index)} tables indexées")

        return index

    def _extract_table_name(self, terminology_name: str) -> Optional[str]:
        """Extrait le nom de table normalisé."""
        # TRE_R48-DiplomeEtatFrancais → TRE-R48-DiplomeEtatFrancais
        # JDV_J01-XdsAuthorSpecialty-CISIS → JDV-J01-XdsAuthorSpecialty-CISIS
        # ASS_A11-CorresModeleCDA → ASS-A11-CorresModeleCDA

        match = re.match(r"^(TRE|JDV|ASS)_([A-Z]\d+)", terminology_name)
        if match:
            return f"{match.group(1)}-{match.group(2)}"

        return None

    def get_stats(self) -> Dict:
        """Retourne les statistiques de cache."""
        total_size = sum(
            Path(meta["file"]).stat().st_size
            for meta in self.metadata["terminologies"].values()
            if Path(meta["file"]).exists()
        )

        return {
            "terminologies_count": len(self.metadata["terminologies"]),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "last_sync": self.metadata.get("last_full_sync"),
            "cache_dir": str(self.cache_dir),
        }

    def check_updates(
        self,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[Dict[str, str]]:
        """
        Vérifie les mises à jour disponibles sans télécharger.

        Args:
            include_patterns: Patterns à inclure
            exclude_patterns: Patterns à exclure

        Returns:
            Liste des référentiels avec mises à jour disponibles
        """
        print("🔍 Vérification des mises à jour disponibles...\n")

        updates_available = []
        checked = 0

        for name, meta in self.metadata["terminologies"].items():
            # Filtrer selon les patterns
            if include_patterns and not any(self._match_pattern(name, p) for p in include_patterns):
                continue
            if exclude_patterns and any(self._match_pattern(name, p) for p in exclude_patterns):
                continue

            checked += 1

            try:
                # Construire l'URL du fichier JSON FHIR
                normalized_name = name.replace("_", "-")
                base_url = urljoin(self.BASE_URL, f"{name}/FHIR/{normalized_name}/")
                json_url = urljoin(base_url, f"{name}-FHIR.json")

                # HEAD request pour obtenir la date
                head_response = httpx.head(json_url, timeout=10.0, follow_redirects=True)
                server_last_modified = head_response.headers.get("Last-Modified")

                if server_last_modified:
                    server_date = parsedate_to_datetime(server_last_modified)
                    local_date_str = meta.get("downloaded_at")

                    if local_date_str:
                        local_date = datetime.fromisoformat(local_date_str)

                        if server_date.replace(tzinfo=None) > local_date:
                            updates_available.append(
                                {
                                    "name": name,
                                    "local_date": local_date.strftime("%Y-%m-%d %H:%M"),
                                    "server_date": server_date.strftime("%Y-%m-%d %H:%M"),
                                    "age_days": (datetime.now() - local_date).days,
                                }
                            )
                            print(f"🔄 {name}: mise à jour disponible")
                            print(f"   Local:  {local_date.strftime('%Y-%m-%d %H:%M')}")
                            print(f"   Serveur: {server_date.strftime('%Y-%m-%d %H:%M')}\n")
                        else:
                            print(f"✅ {name}: à jour")

            except Exception as e:
                print(f"⚠️  {name}: erreur - {e}")

        print("\n📊 Résumé:")
        print(f"   Vérifiés: {checked}")
        print(f"   Mises à jour disponibles: {len(updates_available)}")

        return updates_available


def download_mos_terminologies(
    force: bool = False, include: Optional[List[str]] = None, exclude: Optional[List[str]] = None
) -> Dict[str, int]:
    """
    Fonction helper pour télécharger les référentiels MOS/NOS.

    Args:
        force: Force le téléchargement même si déjà à jour
        include: Patterns à inclure (ex: ["TRE_R*"])
        exclude: Patterns à exclure

    Returns:
        Statistiques de téléchargement

    Example:
        >>> from annuairesante_fhir.mos_downloader import download_mos_terminologies
        >>>
        >>> # Télécharger tous les TRE
        >>> stats = download_mos_terminologies(include=["TRE_*"])
        >>>
        >>> # Télécharger tous sauf les ASS
        >>> stats = download_mos_terminologies(exclude=["ASS_*"])
    """
    downloader = MOSDownloader()
    stats = downloader.download_all(force=force, include_patterns=include, exclude_patterns=exclude)

    # Construire l'index après téléchargement
    if stats["downloaded"] > 0:
        downloader.build_lookup_index()

    return stats
