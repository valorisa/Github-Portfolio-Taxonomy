# ROADMAP — Github-Portfolio-Taxonomy

[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/valorisa/Github-Portfolio-Taxonomy)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Feuille de route des améliorations prévues pour transformer l'outil d'un
script ponctuel en système de classification continu et automatisé.

---

## Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Phase 1 — Friction minimale, bénéfice maximal](#phase-1--friction-minimale-bénéfice-maximal)
- [Phase 2 — Profondeur et précision](#phase-2--profondeur-et-précision)
- [Phase 3 — Nice-to-have](#phase-3--nice-to-have)
- [Tableau de priorisation](#tableau-de-priorisation)
- [Suivi d'avancement](#suivi-davancement)

---

## Vue d'ensemble

### Objectif

Élever `Github-Portfolio-Taxonomy` d'un MVP utile (7/10) vers un système
production-ready pour solo dev et petite équipe (9.5/10), sans complexité
inutile.

### Périmètre des améliorations

```text
Avant : génération manuelle → script ponctuel → outputs statiques
Après : fetch automatique  → CI/CD quotidien → rapports enrichis + historique
```

### Critères de succès globaux

- Zéro friction pour l'utilisateur : 2 commandes max pour un run complet
- Portfolio toujours à jour sans intervention manuelle
- Rapports exploitables : distribution, confiance, diffs
- Code maintenable : chaque amélioration est indépendante et testable

---

## Phase 1 — Friction minimale, bénéfice maximal

> Durée estimée : 1 semaine
> Priorité : 🔴 Critique

### 1.1 Auto-fetch des repositories via GitHub API

**Problème actuel**

L'utilisateur doit générer manuellement `inventory/repos.json` via une
commande `gh api` externe avant chaque run. C'est le principal point de
friction : deux outils distincts, pas d'automatisation possible.

**Solution**

Créer `scripts/fetch-repos.py` : appel direct à l'API GitHub REST, sans
dépendance à GitHub CLI. Authentification par variable d'environnement
`GITHUB_TOKEN`. Support de la pagination complète.

**Fichiers concernés**

- `scripts/fetch-repos.py` ← à créer
- `inventory/repos.json` ← généré automatiquement
- `requirements.txt` ← ajouter `requests`

**Interface cible**

```powershell
# Avant (2 étapes manuelles)
gh api user/repos ... > inventory/repos.json
python scripts/generate-taxonomy.py

# Après (1 commande)
python scripts/fetch-repos.py && python scripts/generate-taxonomy.py
```

**Critères d'acceptation**

- [ ] Authentification par `GITHUB_TOKEN` (env var)
- [ ] Pagination complète (tous les repos, pas seulement les 30 premiers)
- [ ] Filtres optionnels : `--user`, `--org`, `--exclude-forks`,
  `--since YYYY-MM-DD`
- [ ] Output : `inventory/repos.json` au format existant (rétrocompatible)
- [ ] Gestion des erreurs : token invalide, rate limit, réseau indisponible

**Effort estimé** : 2-3 h
**Impact** : 🔴 Élevé — élimine la friction principale du workflow

---

### 1.2 Distribution par domaine dans les statistiques

**Problème actuel**

`reports/statistics.md` rapporte uniquement la couverture globale
(classified / total). Aucune visibilité sur la répartition par domaine :
impossible de savoir si le portfolio est équilibré ou concentré sur un seul
domaine.

**Solution**

Ajouter un tableau de distribution dans `reports/statistics.md` via
`collections.Counter()` sur les topics détectés.

**Fichiers concernés**

- `scripts/generate-taxonomy.py` ← modifier la fonction de stats
- `reports/statistics.md` ← output enrichi

**Output cible**

```markdown
## Domain Distribution

| Domain   | Repositories | Coverage |
|----------|-------------|---------|
| Cloud    | 45          | 26.0%   |
| Backend  | 39          | 22.5%   |
| DevOps   | 38          | 22.0%   |
| Frontend | 28          | 16.2%   |
| AI/ML    | 23          | 13.3%   |
| **Total classified** | **173** | **100%** |
```

**Critères d'acceptation**

- [ ] Tableau trié par nombre de repos décroissant
- [ ] Pourcentage calculé sur les repos classifiés (pas le total)
- [ ] Rétrocompatible : le reste de `statistics.md` reste inchangé
- [ ] Gestion du cas : aucun repo classifié (division par zéro)

**Effort estimé** : 1-2 h
**Impact** : 🟠 Moyen — haute visibilité, effort minimal

---

### 1.3 CI/CD : régénération automatique via GitHub Actions

**Problème actuel**

Le dossier `.github/workflows/` contient uniquement le workflow markdownlint.
Aucune automation pour régénérer la taxonomie : le portfolio se dégrade
silencieusement à chaque nouveau repo créé.

**Solution**

Créer `.github/workflows/taxonomy.yml` : déclenché quotidiennement (cron) et
à chaque modification de `taxonomy/domains.yml`. Exécute fetch + génération +
commit automatique des outputs.

**Fichiers concernés**

- `.github/workflows/taxonomy.yml` ← à créer
- `scripts/fetch-repos.py` ← prérequis : amélioration 1.1

**Workflow cible**

```yaml
on:
  schedule:
    - cron: "0 2 * * *"   # Quotidien à 2h UTC
  push:
    paths:
      - taxonomy/domains.yml
  workflow_dispatch:        # Déclenchement manuel possible
```

**Critères d'acceptation**

- [ ] Déclenchement : cron quotidien + push sur `domains.yml` + manuel
- [ ] Secret `GITHUB_TOKEN` injecté automatiquement (pas de secret custom)
- [ ] Commit automatique uniquement si les outputs ont changé (`git diff`)
- [ ] Message de commit conventionnel : `chore: update taxonomy [skip ci]`
- [ ] Pas de boucle infinie (le commit de mise à jour ne relance pas le
  workflow)

**Effort estimé** : 1-2 h
**Impact** : 🟠 Moyen — automatise entièrement la maintenance

---

## Phase 2 — Profondeur et précision

> Durée estimée : 1 semaine
> Priorité : 🟠 Importante

### 2.1 Scoring de confiance par domaine

**Problème actuel**

Tous les keywords ont le même poids. Un repo contenant le mot `model`
(très générique) est classé AI/ML avec la même confiance qu'un repo
contenant `tensorflow` (très spécifique). Résultat : faux positifs,
classifications trop larges.

**Solution**

Pondérer les keywords dans `taxonomy/domains.yml` (0-100). Calculer un
score de confiance par match. Exposer le score dans `portfolio.json`.
Permettre de filtrer les matches sous un seuil configurable.

**Fichiers concernés**

- `taxonomy/domains.yml` ← ajouter les poids
- `scripts/generate-taxonomy.py` ← modifier la logique de matching
- `inventory/portfolio.json` ← output enrichi avec scores

**Format cible dans `domains.yml`**

```yaml
AI/ML:
  keywords:
    tensorflow: 100
    pytorch: 100
    machine learning: 90
    neural: 80
    model: 50
    data: 30
```

**Output cible dans `portfolio.json`**

```json
{
  "name": "my-ml-project",
  "topics": [
    {"domain": "AI/ML", "confidence": 92},
    {"domain": "Backend", "confidence": 45}
  ]
}
```

**Critères d'acceptation**

- [ ] Format `domains.yml` rétrocompatible (keywords sans poids = 100 par
  défaut)
- [ ] Score de confiance calculé : moyenne pondérée des keywords matchés
- [ ] Seuil de filtrage configurable (défaut : 60%)
- [ ] `unclassified.md` inclut les repos filtrés par seuil (avec leur score)
- [ ] `statistics.md` rapporte la confiance moyenne par domaine

**Effort estimé** : 3-4 h
**Impact** : 🟠 Moyen — réduit les faux positifs, améliore la précision

---

### 2.2 Intégration des topics GitHub natifs

**Problème actuel**

Le script ignore les topics que l'utilisateur a déjà taggés manuellement
sur GitHub (via l'UI ou l'API). Il réinvente la classification sur des repos
déjà bien catégorisés.

**Solution**

Inclure les `topics` GitHub dans `repos.json` lors du fetch. Lors de la
classification : prioriser les topics manuels sur le matching automatique.
La curation manuelle prime toujours sur l'automatique.

**Fichiers concernés**

- `scripts/fetch-repos.py` ← ajouter le champ `topics`
- `scripts/generate-taxonomy.py` ← logique de priorité
- `inventory/repos.json` ← format étendu

**Logique de priorité**

```text
Si repo.topics (GitHub natifs) non vides
  → Utiliser comme classification principale
  → Compléter avec les keywords auto si pertinent
Sinon
  → Matching par keywords uniquement
```

**Critères d'acceptation**

- [ ] `repos.json` inclut le champ `"githubTopics": [...]`
- [ ] Topics GitHub natifs préservés dans `portfolio.json`
- [ ] Distinction dans le rapport : `source: "manual"` vs `source: "auto"`
- [ ] Rétrocompatible : si `githubTopics` absent, fallback sur keywords

**Effort estimé** : 2 h
**Impact** : 🟠 Moyen — respecte la curation existante, réduit le travail

---

## Phase 3 — Nice-to-have

> Durée estimée : 2-3 semaines (selon priorités)
> Priorité : 🟢 Optionnelle

### 3.1 Historique et diffs entre exécutions

**Problème actuel**

Chaque run écrase les outputs. Impossible de savoir ce qui a changé : nouveau
repo classifié, repo passé d'un domaine à un autre, repo supprimé.

**Solution**

Conserver un snapshot horodaté après chaque run. Générer un `changes.md`
comparant le run actuel au précédent.

**Fichiers concernés**

- `scripts/generate-taxonomy.py` ← ajouter la logique de diff
- `reports/changes.md` ← nouveau rapport de diff
- `reports/history/` ← snapshots horodatés (optionnel)

**Output cible dans `changes.md`**

```markdown
## Changes — 2026-06-16

### New repositories classified
- `new-ai-project` → AI/ML (confidence: 87%)

### Domain changes
- `cloud-app` : DevOps → Cloud, DevOps

### Removed from portfolio
- `old-experiment` (deleted or made private)
```

**Critères d'acceptation**

- [ ] Diff calculé entre `portfolio.json` actuel et précédent snapshot
- [ ] Catégories : ajouts, suppressions, changements de domaine
- [ ] Snapshot sauvegardé avec timestamp ISO 8601
- [ ] `changes.md` généré uniquement si des changements existent
- [ ] Option `--no-history` pour désactiver

**Effort estimé** : 3-4 h
**Impact** : 🟢 Moyen — audit trail, détection de régressions

---

### 3.2 Détection de technologies depuis les fichiers du repo

**Problème actuel**

Classification basée uniquement sur le texte (nom + description). Ignore
le contenu réel du repo : langage principal, frameworks détectés depuis
`package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, etc.

**Solution**

Appeler l'API GitHub pour lire les fichiers indicateurs sans cloner le repo.
Déduire les technologies et les injecter dans la classification.

**Fichiers concernés**

- `scripts/detect-tech.py` ← à créer (module séparé)
- `scripts/generate-taxonomy.py` ← intégrer la détection

**Indicateurs de technologie**

| Fichier | Technologies détectées |
|---------|----------------------|
| `package.json` | JavaScript, Node.js, Frontend |
| `requirements.txt` | Python |
| `go.mod` | Go, Backend |
| `Cargo.toml` | Rust |
| `Dockerfile` | DevOps, Container |
| `.github/workflows/` | CI/CD, DevOps |
| `terraform/` | Cloud, Infrastructure |

**Critères d'acceptation**

- [ ] Détection via API GitHub (pas de clone local)
- [ ] Cache des résultats pour éviter les appels répétés
- [ ] Limiter à 1 appel API par repo (rate limit)
- [ ] Rétrocompatible : désactivable via `--no-tech-detect`

**Effort estimé** : 5-6 h
**Impact** : 🟠 Moyen — classification plus précise, mais complexité élevée

---

### 3.3 Filtres et requêtes avancées en CLI

**Problème actuel**

Les rapports sont fixes. Impossible de générer un sous-ensemble : « mes repos
AI/ML actifs des 6 derniers mois, hors forks ».

**Solution**

Ajouter des flags CLI via `argparse` pour filtrer les outputs à la demande.

**Interface cible**

```powershell
python scripts/generate-taxonomy.py `
  --filter-domain "AI/ML" `
  --min-confidence 80 `
  --exclude-forks `
  --since 2026-01-01 `
  --output reports/ai-ml-active.md
```

**Flags prévus**

| Flag | Description |
|------|-------------|
| `--filter-domain DOMAIN` | Filtrer par domaine |
| `--min-confidence N` | Seuil de confiance minimum (0-100) |
| `--exclude-forks` | Exclure les forks |
| `--exclude-private` | Exclure les repos privés |
| `--since YYYY-MM-DD` | Repos modifiés après cette date |
| `--output FILE` | Fichier de sortie personnalisé |

**Critères d'acceptation**

- [ ] Tous les flags sont optionnels (comportement par défaut inchangé)
- [ ] Combinaison de flags possible
- [ ] `--help` documenté et à jour
- [ ] Les outputs filtrés n'écrasent pas les outputs globaux

**Effort estimé** : 2-3 h
**Impact** : 🟢 Bas — utile pour cas d'usage avancés

---

## Tableau de priorisation

| # | Amélioration | Phase | Impact | Effort | Score |
|----|------|-------|--------|--------|-------|
| 1.1 | Auto-fetch repos | 1 | 🔴 Élevé | 🟢 Bas | **9/10** |
| 1.2 | Distribution domaines | 1 | 🟠 Moyen | 🟢 Bas | **8/10** |
| 1.3 | CI/CD GitHub Actions | 1 | 🟠 Moyen | 🟢 Bas | **7/10** |
| 2.1 | Scoring confiance | 2 | 🟠 Moyen | 🟠 Moyen | **7/10** |
| 2.2 | Topics GitHub natifs | 2 | 🟠 Moyen | 🟢 Bas | **7/10** |
| 3.1 | Historique et diffs | 3 | 🟠 Moyen | 🟠 Moyen | **6/10** |
| 3.2 | Détection technologies | 3 | 🟠 Moyen | 🔴 Élevé | **5/10** |
| 3.3 | Filtres CLI avancés | 3 | 🟢 Bas | 🟠 Moyen | **5/10** |

---

## Suivi d'avancement

### Phase 1

- [ ] **1.1** Auto-fetch repos (`scripts/fetch-repos.py`)
- [ ] **1.2** Distribution domaines (`reports/statistics.md`)
- [ ] **1.3** CI/CD taxonomie (`.github/workflows/taxonomy.yml`)

### Phase 2

- [ ] **2.1** Scoring de confiance (`taxonomy/domains.yml` + script)
- [ ] **2.2** Topics GitHub natifs (`fetch-repos.py` + `generate-taxonomy.py`)

### Phase 3

- [ ] **3.1** Historique et diffs (`reports/changes.md`)
- [ ] **3.2** Détection de technologies (`scripts/detect-tech.py`)
- [ ] **3.3** Filtres CLI avancés (`argparse`)

---

## Dépendances entre améliorations

```text
1.1 Auto-fetch
 └─► 1.3 CI/CD          (le workflow appelle fetch-repos.py)
 └─► 2.2 Topics natifs  (fetch-repos.py récupère les topics GitHub)

2.1 Scoring confiance
 └─► 3.3 Filtres CLI    (--min-confidence utilise le scoring)

1.1 + 2.1
 └─► 3.1 Historique     (diff pertinent uniquement avec fetch auto + scores)
```

---

## Contribution

Pour implémenter une amélioration :

1. Créer une branche : `git checkout -b feat/1.1-auto-fetch`
2. Implémenter selon les critères d'acceptation de la section concernée
3. Tester localement avant PR
4. Référencer le numéro d'amélioration dans le message de commit :
   `feat(1.1): add fetch-repos.py with pagination and token auth`

---

*Roadmap générée le 2026-06-16 — mise à jour à chaque sprint.*
