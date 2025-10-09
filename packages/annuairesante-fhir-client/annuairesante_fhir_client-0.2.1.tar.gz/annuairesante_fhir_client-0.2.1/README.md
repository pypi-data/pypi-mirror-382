# Annuaire Santé FHIR Client

Client Python pour l'API FHIR de l'Annuaire Santé (ANS).

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

## Caractéristiques

- ✅ Support complet des ressources FHIR de l'Annuaire Santé
- ✅ **Helper dynamique adaptatif** - s'adapte automatiquement à la structure FHIR
- ✅ **Helpers statiques** pour accès rapide aux données courantes
- ✅ **Résolution automatique des codes MOS**
- ✅ Pagination automatique via liens `next`
- ✅ Gestion d'erreurs robuste
- ✅ Types stricts avec Pydantic
- ✅ Context manager pour gestion automatique des connexions
- ✅ Tests unitaires complets

## Installation

```bash
pip install annuairesante-fhir-client
```

## Configuration

Créez un fichier `.env` à la racine du projet :

```env
ANNUAIRE_SANTE_API_KEY=votre_clé_api

# Optionnel: Configurer le répertoire de cache MOS
# Par défaut: ~/.annuairesante_cache
ANNUAIRE_SANTE_CACHE_DIR=/chemin/vers/cache

# Optionnel: Initialiser automatiquement le cache MOS au premier import
# Par défaut: false
ANNUAIRE_SANTE_AUTO_INIT_MOS=true
```

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `ANNUAIRE_SANTE_API_KEY` | Clé API pour l'Annuaire Santé (obligatoire) | - |
| `ANNUAIRE_SANTE_CACHE_DIR` | Répertoire pour le cache MOS/NOS | `~/.annuairesante_cache` |
| `ANNUAIRE_SANTE_AUTO_INIT_MOS` | Télécharger automatiquement les référentiels MOS au premier import | `false` |

**Note sur l'auto-initialisation MOS**: Lorsque `ANNUAIRE_SANTE_AUTO_INIT_MOS=true`, la librairie téléchargera automatiquement les référentiels MOS essentiels (tables TRE_R*) lors du premier import si le cache est vide. Cela peut prendre quelques minutes mais ne se fera qu'une seule fois.

## Démarrage rapide

### Avec le helper statique (extraction simple) ⭐

```python
from annuairesante_fhir import AnnuaireSanteClient
from annuairesante_fhir.helpers import wrap_practitioner

with AnnuaireSanteClient() as client:
    # Rechercher des professionnels
    result = client.practitioner.search(family="Dupont")

    # Helper statique - propriétés simplifiées
    p = wrap_practitioner(result.entries[0])

    # Accès simple aux propriétés courantes
    print(f"{p.name} (RPPS: {p.rpps})")
    print(f"Genre: {p.gender}, Actif: {p.active}")
    print(f"Email: {p.email}")
```

### Avec le helper dynamique (accès FHIR complet)

```python
from annuairesante_fhir import AnnuaireSanteClient
from annuairesante_fhir.dynamic_helper import fhir

with AnnuaireSanteClient() as client:
    result = client.practitioner.search(family="Dupont")

    # Helper dynamique - accès FHIR direct avec wrapping récursif
    p = fhir(result.entries[0], auto_resolve_mos=True)

    # Accès avec notation pointée aux structures FHIR
    print(f"Nom: {p.name[0].family} {' '.join(p.name[0].given)}")
    print(f"Genre: {p.gender}, Actif: {p.active}")
    print(f"RPPS: {p.identifier[0].value}")
```

### Pagination automatique

```python
from annuairesante_fhir import AnnuaireSanteClient
from annuairesante_fhir.helpers import wrap_practitioner

with AnnuaireSanteClient() as client:
    # Recherche simple
    result = client.practitioner.search(family="Dupont")
    for entry in result.entries:
        p = wrap_practitioner(entry)
        print(f"- {p.name} (RPPS: {p.rpps})")

    # Pagination automatique (récupère tous les résultats)
    all_results = client.practitioner.search_all(
        family="Martin",
        max_results=100
    )
    print(f"Récupéré {len(all_results)} résultats")
```

## Ressources supportées

| Ressource | Description | Recherches principales |
|-----------|-------------|------------------------|
| **Practitioner** | Professionnels de santé | family, given, identifier, active |
| **Organization** | Structures de santé | name, identifier, address_city, active |
| **PractitionerRole** | Rôles des professionnels | practitioner, organization, role, active |
| **HealthcareService** | Services de santé | name, organization, service_type |
| **Device** | Équipements médicaux | identifier, type, status |

## Quelle approche choisir ?

### Helper Statique (extraction simple) ⭐
✅ Propriétés simplifiées prêtes à l'emploi (rpps, name, email)
✅ Autocomplétion IDE complète
✅ Moins de code pour les cas courants

```python
from annuairesante_fhir.helpers import wrap_practitioner
p = wrap_practitioner(data)
print(f"{p.name}: {p.rpps}")  # Simple et direct
print(f"Email: {p.email}")
```

### Helper Dynamique (accès FHIR complet)
✅ Accès automatique à tous les champs FHIR
✅ Wrapping récursif des structures imbriquées
✅ Résolution MOS automatique intégrée
✅ Future-proof - nouveaux champs automatiquement accessibles

```python
from annuairesante_fhir.dynamic_helper import fhir
p = fhir(data, auto_resolve_mos=True)
print(p.name[0].family)  # Accès FHIR direct
print(p.gender, p.birthDate)  # Tous les champs FHIR
```

📖 [Comparaison détaillée](DYNAMIC_VS_STATIC.md)

## Documentation

📚 **Guides** :
- [QUICKSTART.md](QUICKSTART.md) - Guide de démarrage rapide
- [GUIDE_HELPERS.md](GUIDE_HELPERS.md) - Helpers statiques et résolution codes MOS
- [GUIDE_DYNAMIC_HELPER.md](GUIDE_DYNAMIC_HELPER.md) - Helper dynamique adaptatif
- [DYNAMIC_VS_STATIC.md](DYNAMIC_VS_STATIC.md) - Comparaison des deux approches
- [CHANGELOG.md](CHANGELOG.md) - Historique des versions

📁 **Exemples** :
- [examples/exemple_simple.py](examples/exemple_simple.py) - Exemple minimaliste
- [examples/basic_usage.py](examples/basic_usage.py) - Exemples de base (recherche, pagination)
- [examples/utilisation_helpers.py](examples/utilisation_helpers.py) - Helpers statiques et codes MOS
- [examples/dynamic_helper_demo.py](examples/dynamic_helper_demo.py) - Helper dynamique

🔗 **Références officielles** :
- [Documentation API ANS](https://ansforge.github.io/annuaire-sante-fhir-documentation/)
- [Guide d'implémentation FHIR](https://interop.esante.gouv.fr/ig/fhir/annuaire/)
- [Dépôt GitHub ANS](https://github.com/ansforge/annuaire-sante-fhir-documentation)

## Tests

```bash
# Lancer les tests
pytest tests/ -v

# Avec coverage
pytest tests/ --cov=annuairesante_fhir
```

## Notes importantes

⚠️ **Pagination** : L'API Annuaire Santé ne supporte pas les paramètres `_count` et `_offset`. La pagination se fait via les liens `next` dans les réponses Bundle (~50 résultats par page).

⚠️ **Format des résultats** : Les méthodes `search()` retournent des dictionnaires Python (pas des objets FHIR strictement validés) pour plus de flexibilité avec les extensions ANS.

## Licence

Ce projet est un client non-officiel pour l'API Annuaire Santé.
