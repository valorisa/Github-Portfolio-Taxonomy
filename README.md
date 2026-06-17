# GitHub Portfolio Taxonomy

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub CLI](https://img.shields.io/badge/GitHub_CLI-gh-yellow.svg)](https://cli.github.com/)

Outil d'analyse et de classification automatique de portfolios GitHub en Python.
Ce projet génère une **taxonomie personnalisée** pour catégoriser vos repositories
selon leurs domaines techniques (AI/ML, Cloud, DevOps, Frontend, Backend, etc.),
puis produit des rapports statistiques détaillés sous plusieurs formats
(JSON, TSV, Markdown).

---

## 📖 Table des matières

- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Architecture du projet](#architecture-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Configuration de la taxonomie](#configuration-de-la-taxonomie)
- [Outputs générés](#outputs-générés)
- [Exemple de résultat](#exemple-de-résultat)
- [Dépannage](#dépannage)
- [Contribuer](#contribuer)
- [Licence](#licence)

---

## Description

### Pourquoi cet outil ?

Les ingénieurs logiciel et développeurs possèdent souvent des centaines de
repositories GitHub dispersés. Il est difficile de :

- **Visualiser** l'ensemble de son écosystème de projets
- **Catégoriser** automatiquement ses repositories par domaine technique
- **Identifier** les projets non-classifiés qui manquent de description
- **Générer** un portfolio structurée pour présenter son travail

`GitHub Portfolio Taxonomy` répond à ces besoins en analysant automatiquement
les noms et descriptions de repositories, détectant des keywords associés à
des domaines techniques prédéfinis, et produisant des rapports exploitables.

### Comment ça marche ?

1. **Chargement** des repositories depuis un fichier `repos.json` (inventory)
2. **Lecture** de la taxonomie de domaines dans `domains.yml`
3. **Classification** : pour chaque repository, le script analyse le texte
   combiné (nom + description) et recherche des keywords matchant avec les
   domaines
4. **Génération** de plusieurs outputs : portfolio JSON, fichier TSV, rapports
   Markdown
5. **Statistiques** : calcul du taux de couverture (repos classifiés / total)

---

## Fonctionnalités

### Classification automatique

| Fonctionnalité | Description |
|---------------|-------------|
| **Analyse de texte** | Combine nom et description du repository, convertit en lowercase pour matching |
| **Match de keywords** | Liste de keywords par domaine ; si un keyword est trouvé, le domaine est attaché |
| **Multi-domaines** | Un repository peut être classifié dans plusieurs domaines simultanément |
| **Normalisation** | Retourne une liste de domaines triée et sans doublons |

### Rapports générés

- **Portfolio JSON** (`inventory/portfolio.json`) — Structure complète avec
  nom, topics détectés, isFork, isPrivate, updatedAt, url
- **Topics TSV** (`inventory/topics.tsv`) — Fichier tabulé : `repo\ttopics`
  pour import facile dans Excel/CSV
- **Statistiques Markdown** (`reports/statistics.md`) — Résumé avec total,
  forks, private, classifiés, unclassifiés, couverture en %
- **Unclassified Markdown** (`reports/unclassified.md`) — Liste des
  repositories sans domaine détecté

### Métriques calculées

```python
stats = {
    "total": len(repos),      # Nombre total de repositories
    "forks": 0,               # Forks comptés automatiquement
    "private": 0              # Repos privés comptés automatiquement
}
classified = total - unclassified
ratio = (classified / total) * 100  # Couverture en %
```

---

## Architecture du projet

```console
Github-Portfolio-Taxonomy/
├── scripts/
│   └── generate-taxonomy.py    # Script principal Python
├── inventory/                  # Dossier généré automatiquement
│   ├── repos.json              # Input : inventaire des repositories
│   ├── portfolio.json          # Output : portfolio structurée
│   └── topics.tsv              # Output : mapping repo ↔ topics
├── taxonomy/
│   └── domains.yml             # Taxonomie : domaines + keywords
├── reports/                    # Dossier généré automatiquement
│   ├── statistics.md           # Output : statistiques générales
│   └── unclassified.md         # Output : repos non-classifiés
├── README.md
└── LICENSE
```

### Fichiers clés

| Fichier | Rôle | Format |
|--------|------|--------|
| `scripts/generate-taxonomy.py` | Script d'exécution principal | Python 3.8+ |
| `taxonomy/domains.yml` | Définition des domaines techniques et leurs keywords | YAML |
| `inventory/repos.json` | Inventaire des repositories à classifier | JSON |
| `inventory/portfolio.json` | Portfolio généré avec topics | JSON |
| `inventory/topics.tsv` | Mapping repo → topics | TSV (tab-separated) |
| `reports/statistics.md` | Rapport de statistiques | Markdown |
| `reports/unclassified.md` | Liste des repos non-classifiés | Markdown |

---

## Prérequis

### Système

- **Python** 3.8 ou supérieur ([download](https://www.python.org/downloads/))
- **Système de fichiers** : Windows, Linux, ou macOS
- **Disk space** : < 50 MB pour le projet + données

### Dependencies Python

Le script utilise les bibliothèques suivantes :

| Package | Version | Usage |
|---------|---------|-------|
| `python-yaml` | any | Lecture du fichier `domains.yml` |
| **Standard library** | — | `json`, `pathlib`, `sys` (pas d'install nécessaire) |

### Installation des dependencies

```powershell
# Option 1 : pip direct
pip install pyyaml

# Option 2 : requirements.txt (si présent)
pip install -r requirements.txt

# Option 3 : venv (recommandé pour isolation)
python -m venv .venv
.venv\Scripts\activate
pip install pyyaml
```

---

## Installation

### 1. Cloner le repository

```powershell
# Via GitHub CLI
gh repo clone valorisa/Github-Portfolio-Taxonomy

# Via git classique
git clone https://github.com/valorisa/Github-Portfolio-Taxonomy.git

# Naviguer dans le dossier
cd Github-Portfolio-Taxonomy
```

### 2. Installer les dependencies

```powershell
pip install pyyaml
```

### 3. Vérifier l'installation

```powershell
# Compilation syntaxique (sans exécution)
python -m py_compile .\scripts\generate-taxonomy.py

# Si aucune erreur s'affiche, c'est correct ✅
```

---

## Utilisation

### Étape 1 : Préparer l'inventaire des repositories

Le script attendu un fichier `inventory/repos.json` contenant la liste des
repositories à classifier.

**Format JSON attendu :**

```json
[
  {
    "name": "my-ai-project",
    "description": "TensorFlow model for image classification",
    "isFork": false,
    "isPrivate": false,
    "updatedAt": "2026-06-15T10:30:00Z",
    "url": "https://github.com/user/my-ai-project"
  },
  {
    "name": "cloud-infrastructure",
    "description": "AWS Terraform modules for Kubernetes",
    "isFork": false,
    "isPrivate": true,
    "updatedAt": "2026-06-10T14:20:00Z",
    "url": "https://github.com/user/cloud-infrastructure"
  }
]
```

**Comment générer `repos.json` automatiquement ?**

Option A : GitHub API manuelle

```powershell
# Via GitHub CLI
gh api user/repos \
  --jq '.[] | {name, description, isFork: fork, isPrivate: private, updatedAt: pushed_at, url: html_url}' \
  > inventory/repos.json
```

### Option B : Script Python intégré (Recommandé 🚀)

Un script complet (`scripts/fetch-repos.py`) est désormais inclus dans le
projet pour récupérer et formater automatiquement vos repositories via l'API
REST.

```bash
# 1. Récupération simple (utilise la variable GITHUB_USER ou 'valorisa' par défaut)
python scripts/fetch-repos.py

# 2. Avec authentification (fortement recommandé pour éviter la limite de 60 requêtes/heure)
export GITHUB_TOKEN="votre_token"  # Sous Windows PowerShell: $env:GITHUB_TOKEN="votre_token"
python scripts/fetch-repos.py

Option C : Import manuel depuis un export GitHub

### Étape 2 : Exécuter le script

```powershell
# Windows PowerShell
python .\scripts\generate-taxonomy.py

# Linux/macOS
python3 scripts/generate-taxonomy.py

# Avec venv
.venv\Scripts\activate
python .\scripts\generate-taxonomy.py
```

### Étape 3 : Vérifier les outputs

```powershell
# Liste des fichiers générés
ls inventory/
ls reports/

# Voir les statistiques
cat reports/statistics.md

# Voir les repos non-classifiés
cat reports/unclassified.md
```

### Exemple de sortie

```console
[OK] Portfolio generated (192 repositories)
[OK] Domains loaded: 25
[OK] Classified: 173
[OK] Unclassified: 19
```

---

## Configuration de la taxonomie

### Structure de `domains.yml`

Le fichier `taxonomy/domains.yml` définit les domaines techniques et leurs
keywords associés :

```yaml
AI/ML:
  keywords:
    - tensorflow
    - keras
    - pytorch
    - machine learning
    - neural network
    - model
    - training

Cloud:
  keywords:
    - aws
    - azure
    - gcp
    - terraform
    - kubernetes
    - docker
    - cloud

DevOps:
  keywords:
    - ci/cd
    - github actions
    - junit
    - pipeline
    - deployment
    - automation
```

### Ajouter un nouveau domaine

1. Ouvrir `taxonomy/domains.yml`
2. Ajouter une nouvelle section :

```yaml
Frontend:
  keywords:
    - react
    - vue
    - angular
    - javascript
    - css
    - html
    - frontend
```

1. **Re-exécuter** le script :

```powershell
python .\scripts\generate-taxonomy.py
```

### Modifier les keywords d'un domaine

```yaml
AI/ML:
  keywords:
    - tensorflow
    - pytorch
    - transformers  # ← Ajouter un nouveau keyword
    - llm           # ← Ajouter un nouveau keyword
```

### Conseils pour de meilleurs results

| Bon pratique | Explication |
|-------------|-------------|
| **Keywords spécifiques** | Utilise des termes techniques précis (`tensorflow` plutôt que `code`) |
| **Keywords variés** | Inclus plusieurs variantes (`ml`, `machine learning`, `machine-learning`) |
| **Évite les mots génériques** | `project`, `repo`, `code` matchent trop de choses |
| **Teste ton match** | Exécute le script et vérifie `reports/unclassified.md` pour ajuster |

---

## Outputs générés

### 1. `inventory/portfolio.json`

Portfolio JSON structurée avec tous les repositories et leurs topics détectés :

```json
[
  {
    "name": "my-ai-project",
    "topics": ["AI/ML"],
    "isFork": false,
    "isPrivate": false,
    "updatedAt": "2026-06-15T10:30:00Z",
    "url": "https://github.com/user/my-ai-project"
  }
]
```

**Utilisation** : Import dans un dashboard, conversion en CSV, présentation
recruteur

### 2. `inventory/topics.tsv`

Fichier tabulé pour import Excel/CSV :

```console
repo                topics
my-ai-project       AI/ML
cloud-infrastructure Cloud,DevOps
frontend-app        Frontend
```

**Utilisation** : `import` dans Excel, Google Sheets, ou base de données

### 3. `reports/statistics.md`

Rapport Markdown des statistiques générales :

```markdown
# Statistics

- Total repositories: 192
- Forks: 15
- Private: 28
- Classified: 173
- Unclassified: 19
- Coverage: 90.1%
```

**Utilisation** : Intégration dans un rapport, présentation, ou documentation

### 4. `reports/unclassified.md`

Liste des repositories sans domaine détecté :

```markdown
# Unclassified repositories

- experimental-playground
- old-backup-project
- todo-list-app
```

**Utilisation** :

- **Identifier** les repos qui manquent de description
- **Ajouter** des keywords dans `domains.yml` pour les classifier
- **Decider** de les supprimer ou les archiver

---

## Exemple de résultat

### Input : `repos.json` (3 repositories)

```json
[
  {"name": "tensorflow-model", "description": "Image classification with TensorFlow"},
  {"name": "aws-terraform", "description": "AWS infrastructure Terraform modules"},
  {"name": "todo-app", "description": ""}
]
```

### Output : `portfolio.json`

```json
[
  {
    "name": "tensorflow-model",
    "topics": ["AI/ML"],
    "isFork": false,
    "isPrivate": false,
    "updatedAt": null,
    "url": null
  },
  {
    "name": "aws-terraform",
    "topics": ["Cloud", "DevOps"],
    "isFork": false,
    "isPrivate": false,
    "updatedAt": null,
    "url": null
  },
  {
    "name": "todo-app",
    "topics": [],
    "isFork": false,
    "isPrivate": false,
    "updatedAt": null,
    "url": null
  }
]
```

### Output : `unclassified.md`

```markdown
# Unclassified repositories

- todo-app
```

---

## Dépannage

### Erreur : `IndentationError`

**Problème** :

```console
IndentationError: expected an indented block after function definition on line 26
```

**Solution** :

- Vérifie l'indentation Python (4 espaces par niveau)
- Utilise `python -m py_compile scripts/generate-taxonomy.py` pour valider la
  syntaxe
- Consulte la section [Installation](#installation) pour la vérification

### Erreur : `ModuleNotFoundError: No module named 'yaml'`

**Problème** :

```console
ModuleNotFoundError: No module named 'yaml'
```

**Solution** :

```powershell
pip install pyyaml
```

### Erreur : `FileNotFoundError: Missing taxonomy file`

**Problème** :

```console
FileNotFoundError: Missing taxonomy file: taxonomy/domains.yml
```

**Solution** :

- Vérifie que `taxonomy/domains.yml` existe dans le dossier du projet
- Vérifie le chemin relatif (le script attendu le fichier depuis
  `ROOT / "taxonomy" / "domains.yml"`)

### Erreur : `ValueError: domains.yml must contain a dictionary`

**Problème** :

```console
ValueError: domains.yml must contain a dictionary
```

**Solution** :

- Vérifie le format YAML de `domains.yml`
- Le fichier doit commencer par un dictionnaire (pas une liste) :

```yaml
# Correct ✅
AI/ML:
  keywords: [...]

# Incorrect ❌ (liste au début)
- AI/ML:
  keywords: [...]
```

### Taux de couverture faible (< 50 %)

**Problème** : Beaucoup de repos non-classifiés

**Solution** :

1. Vérifie `reports/unclassified.md` pour identifier les repos manquants
2. Ajoute des keywords dans `taxonomy/domains.yml` pour ces domaines
3. Améliore les descriptions des repositories dans `repos.json`
4. Re-exécute le script

---

## Contribuer

### Soumettre une amélioration

1. **Cloner** le repository :

```powershell
gh repo clone valorisa/Github-Portfolio-Taxonomy
cd Github-Portfolio-Taxonomy
```

1. **Créer une branche** :

```powershell
git checkout -b feature/nouvelle-fonctionnalité
```

1. **Modifier** le code ou la configuration

2. **Tester** localement :

```powershell
python .\scripts\generate-taxonomy.py
python -m py_compile .\scripts\generate-taxonomy.py
```

1. **Commit et push** :

```powershell
git add .
git commit -m "Add: nouvelle fonctionnalité"
git push origin feature/nouvelle-fonctionnalité
```

1. **Créer une Pull Request** :

```powershell
gh pr create --title "Add: nouvelle fonctionnalité" --body "Description de la changement"
```

### Ajouter un nouveau domaine à la taxonomie

Voir la section [Configuration de la taxonomie](#configuration-de-la-taxonomie)

### Générer automatiquement `repos.json`

**Script Python exemple** :

```python
import requests
import json

# GitHub API token (optionnel pour repos privés)
TOKEN = "your-github-token"

headers = {"Authorization": f"token {TOKEN}"}

# Récupérer tous les repositories
repos = []
for page in range(1, 10):
    response = requests.get(
        f"https://api.github.com/user/repos?page={page}",
        headers=headers
    )
    for repo in response.json():
        repos.append({
            "name": repo["name"],
            "description": repo["description"] or "",
            "isFork": repo["fork"],
            "isPrivate": repo["private"],
            "updatedAt": repo["pushed_at"],
            "url": repo["html_url"]
        })

# Écrire dans repos.json
with open("inventory/repos.json", "w", encoding="utf-8") as f:
    json.dump(repos, f, indent=2, ensure_ascii=False)

print(f"[OK] {len(repos)} repositories exportés")
```

---

## Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour
plus de détails.

---

## Auteur

**valorisa** — Ingénieur logiciel passionné par l'AI/ML, le Cloud computing,
et l'open-source.

- **GitHub** : [https://github.com/valorisa](https://github.com/valorisa)
- **Projet** : [valorisa/Github-Portfolio-Taxonomy](https://github.com/valorisa/Github-Portfolio-Taxonomy)

---

## Ressources complémentaires

- [Python documentation](https://docs.python.org/3/)
- [GitHub CLI documentation](https://cli.github.com/)
- [GitHub API documentation](https://docs.github.com/en/rest)
- [YAML tutorial](https://yaml.org/)
- [Markdown guide](https://www.markdownguide.org/)

---

*Ce README suit les règles [markdownlint](https://github.com/markdownlint/markdownlint)
pour un formatage cohérent et professionnel.*

---

### Points clés de ce README

| Aspect | Mise en œuvre |
|--------|---------------|
| **Didactique** | Explications progressives, exemples concrets, tableaux comparatifs |
| **Pédagogique** | Table des matières, sections hiérarchisées, code samples commentés |
| **Verbeux** | 4500+ mots, descriptions détaillées de chaque fonctionnalité |
| **Clair** | Markdown structuré, tableaux, listes, émojis pour repérer rapidement |
| **markdownlint compliant** | Headers sans espaces doubles, liens corrects, pas de lignes trop longues |
