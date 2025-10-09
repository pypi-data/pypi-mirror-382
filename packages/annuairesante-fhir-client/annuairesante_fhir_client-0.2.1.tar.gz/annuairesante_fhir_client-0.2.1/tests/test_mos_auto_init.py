"""Tests pour l'initialisation automatique du cache MOS."""

import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestMOSAutoInit:
    """Tests pour l'auto-initialisation du cache MOS."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Crée un répertoire de cache temporaire."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Nettoyage
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def clean_env(self):
        """Sauvegarde et restaure les variables d'environnement."""
        old_cache_dir = os.environ.get("ANNUAIRE_SANTE_CACHE_DIR")
        old_auto_init = os.environ.get("ANNUAIRE_SANTE_AUTO_INIT_MOS")

        yield

        # Restaurer
        if old_cache_dir is not None:
            os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = old_cache_dir
        else:
            os.environ.pop("ANNUAIRE_SANTE_CACHE_DIR", None)

        if old_auto_init is not None:
            os.environ["ANNUAIRE_SANTE_AUTO_INIT_MOS"] = old_auto_init
        else:
            os.environ.pop("ANNUAIRE_SANTE_AUTO_INIT_MOS", None)

    def test_cache_dir_from_env(self, temp_cache_dir, clean_env):
        """Test que le cache utilise le répertoire de la variable d'environnement."""
        from annuairesante_fhir.mos_resolver import MOSResolver

        os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = temp_cache_dir

        resolver = MOSResolver()

        assert resolver.cache_dir == Path(temp_cache_dir)
        assert resolver.cache_dir.exists()

    def test_cache_dir_default(self, clean_env):
        """Test que le cache utilise le répertoire par défaut si aucune variable."""
        from annuairesante_fhir.mos_resolver import MOSResolver

        # S'assurer qu'aucune variable n'est définie
        os.environ.pop("ANNUAIRE_SANTE_CACHE_DIR", None)

        resolver = MOSResolver()

        expected = Path.home() / ".annuairesante_cache"
        assert resolver.cache_dir == expected

    def test_auto_init_disabled_by_default(self, temp_cache_dir, clean_env):
        """Test que l'auto-init n'est pas activée par défaut."""
        from annuairesante_fhir.mos_resolver import MOSResolver

        os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = temp_cache_dir
        os.environ.pop("ANNUAIRE_SANTE_AUTO_INIT_MOS", None)

        with patch.object(MOSResolver, "_auto_init_cache") as mock_auto_init:
            resolver = MOSResolver()

            # _auto_init_cache ne doit PAS être appelé
            mock_auto_init.assert_not_called()
            assert resolver._mos_index is None

    def test_auto_init_enabled_true(self, temp_cache_dir, clean_env):
        """Test que l'auto-init se déclenche quand ANNUAIRE_SANTE_AUTO_INIT_MOS=true."""
        from annuairesante_fhir.mos_resolver import MOSResolver

        os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = temp_cache_dir
        os.environ["ANNUAIRE_SANTE_AUTO_INIT_MOS"] = "true"

        with patch.object(MOSResolver, "_auto_init_cache") as mock_auto_init:
            resolver = MOSResolver()

            # _auto_init_cache doit être appelé
            mock_auto_init.assert_called_once()

    def test_auto_init_enabled_variations(self, temp_cache_dir, clean_env):
        """Test les différentes valeurs acceptées pour activer l'auto-init."""
        from annuairesante_fhir.mos_resolver import MOSResolver

        os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = temp_cache_dir

        # Tester différentes valeurs
        for value in ["true", "TRUE", "True", "1", "yes", "YES", "Yes"]:
            os.environ["ANNUAIRE_SANTE_AUTO_INIT_MOS"] = value

            with patch.object(MOSResolver, "_auto_init_cache") as mock_auto_init:
                resolver = MOSResolver()
                mock_auto_init.assert_called_once()

    def test_auto_init_disabled_variations(self, temp_cache_dir, clean_env):
        """Test les valeurs qui désactivent l'auto-init."""
        from annuairesante_fhir.mos_resolver import MOSResolver

        os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = temp_cache_dir

        # Tester différentes valeurs
        for value in ["false", "FALSE", "False", "0", "no", "NO", "No", ""]:
            os.environ["ANNUAIRE_SANTE_AUTO_INIT_MOS"] = value

            with patch.object(MOSResolver, "_auto_init_cache") as mock_auto_init:
                resolver = MOSResolver()
                mock_auto_init.assert_not_called()

    def test_auto_init_cache_exists_skip(self, temp_cache_dir, clean_env):
        """Test que l'auto-init ne se déclenche pas si le cache existe déjà."""
        from annuairesante_fhir.mos_resolver import MOSResolver

        os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = temp_cache_dir
        os.environ["ANNUAIRE_SANTE_AUTO_INIT_MOS"] = "true"

        # Créer un index factice
        mos_dir = Path(temp_cache_dir) / "mos"
        mos_dir.mkdir(parents=True)
        index_file = mos_dir / "lookup_index.json"
        index_file.write_text(json.dumps({"TRE-R01": {"code1": "display1"}}))

        with patch.object(MOSResolver, "_auto_init_cache") as mock_auto_init:
            resolver = MOSResolver()

            # _auto_init_cache ne doit PAS être appelé car l'index existe
            mock_auto_init.assert_not_called()
            assert resolver._mos_index is not None
            assert "TRE-R01" in resolver._mos_index

    def test_auto_init_cache_downloads(self, temp_cache_dir, clean_env):
        """Test que _auto_init_cache télécharge les référentiels."""
        from annuairesante_fhir.mos_resolver import MOSResolver

        os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = temp_cache_dir

        # Mock du downloader au niveau du module mos_downloader
        with patch("annuairesante_fhir.mos_downloader.MOSDownloader") as mock_downloader_class:
            mock_downloader = MagicMock()
            mock_downloader.download_all.return_value = {"downloaded": 10, "skipped": 0, "errors": 0}
            mock_downloader_class.return_value = mock_downloader

            resolver = MOSResolver()

            # Appeler manuellement _auto_init_cache
            resolver._auto_init_cache()

            # Vérifier que MOSDownloader a été instancié avec le bon cache_dir
            mock_downloader_class.assert_called_once()
            call_kwargs = mock_downloader_class.call_args[1]
            assert call_kwargs["cache_dir"] == str(Path(temp_cache_dir) / "mos")

            # Vérifier que download_all a été appelé avec les bons paramètres
            mock_downloader.download_all.assert_called_once()
            call_kwargs = mock_downloader.download_all.call_args[1]
            assert call_kwargs["force"] is False
            assert call_kwargs["include_patterns"] == ["TRE_R*"]

    def test_auto_init_cache_error_handling(self, temp_cache_dir, clean_env):
        """Test que les erreurs lors de l'auto-init sont gérées."""
        from annuairesante_fhir.mos_resolver import MOSResolver

        os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = temp_cache_dir

        # Mock du downloader qui lève une exception au niveau du module
        with patch("annuairesante_fhir.mos_downloader.MOSDownloader") as mock_downloader_class:
            mock_downloader_class.side_effect = Exception("Erreur réseau")

            resolver = MOSResolver()

            # _auto_init_cache ne doit pas faire crasher
            resolver._auto_init_cache()

            # L'index doit rester None
            assert resolver._mos_index is None

    def test_mos_downloader_uses_env_cache_dir(self, temp_cache_dir, clean_env):
        """Test que MOSDownloader utilise la variable d'environnement."""
        from annuairesante_fhir.mos_downloader import MOSDownloader

        os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = temp_cache_dir

        downloader = MOSDownloader()

        assert downloader.cache_dir == Path(temp_cache_dir) / "mos"
        assert downloader.cache_dir.exists()

    def test_mos_downloader_default_cache_dir(self, clean_env):
        """Test que MOSDownloader utilise le répertoire par défaut."""
        from annuairesante_fhir.mos_downloader import MOSDownloader

        os.environ.pop("ANNUAIRE_SANTE_CACHE_DIR", None)

        downloader = MOSDownloader()

        expected = Path.home() / ".annuairesante_cache" / "mos"
        assert downloader.cache_dir == expected

    def test_mos_downloader_explicit_cache_dir(self, temp_cache_dir):
        """Test que le paramètre explicite prend le dessus sur la variable d'environnement."""
        from annuairesante_fhir.mos_downloader import MOSDownloader

        os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = "/autre/chemin"

        downloader = MOSDownloader(cache_dir=temp_cache_dir)

        # Le paramètre explicite doit prendre le dessus
        assert downloader.cache_dir == Path(temp_cache_dir)

    def test_integration_full_workflow(self, temp_cache_dir, clean_env):
        """Test d'intégration du workflow complet avec cache vide."""
        from annuairesante_fhir.mos_downloader import MOSDownloader
        from annuairesante_fhir.mos_resolver import MOSResolver

        os.environ["ANNUAIRE_SANTE_CACHE_DIR"] = temp_cache_dir

        # 1. Créer un downloader et simuler un téléchargement
        downloader = MOSDownloader()

        # Créer un index factice
        mos_dir = Path(temp_cache_dir) / "mos"
        mos_dir.mkdir(parents=True, exist_ok=True)
        index_file = mos_dir / "lookup_index.json"

        fake_index = {
            "TRE-R48": {"DE01": "Diplôme 1", "DE02": "Diplôme 2"},
            "TRE-R85": {"G01": "Genre 1", "G02": "Genre 2"},
        }
        index_file.write_text(json.dumps(fake_index, ensure_ascii=False))

        # 2. Créer un resolver qui doit charger cet index
        resolver = MOSResolver()

        # 3. Vérifier que l'index est chargé
        assert resolver._mos_index is not None
        assert "TRE-R48" in resolver._mos_index
        assert "TRE-R85" in resolver._mos_index

        # 4. Tester la résolution d'un code
        result = resolver.resolve(
            "https://mos.esante.gouv.fr/NOS/TRE_R48-DiplomeEtatFrancais/FHIR/TRE-R48-DiplomeEtatFrancais",
            "DE01",
        )
        assert result == "Diplôme 1"

        # 5. Vérifier les stats
        stats = resolver.get_stats()
        assert stats["loaded"] is True
        assert stats["tables_count"] == 2
        assert stats["total_codes"] == 4
