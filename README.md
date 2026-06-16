# Github-Portfolio-Taxonomy

Portfolio Governance System for GitHub repositories.

This repository centralizes governance, taxonomy, reporting, and topic management for all repositories owned by `valorisa`.

## Objectives

* Maintain a consistent taxonomy across repositories.
* Generate GitHub topics automatically.
* Produce portfolio-wide reports.
* Detect unclassified repositories.
* Track repository evolution.
* Separate original projects from forks.
* Generate a navigable catalog.

---

## Repository Structure

```text
github-portfolio/

├── taxonomy/
│   ├── domains.yml
│   ├── rules.yml
│
├── inventory/
│   ├── repos.json
│   ├── portfolio.json
│   ├── topics.tsv
│
├── reports/
│   ├── statistics.md
│   ├── stale.md
│   ├── unclassified.md
│
├── scripts/
│   ├── collect-repos.py
│   ├── generate-taxonomy.py
│   ├── apply-topics.py
│   ├── validate-taxonomy.py
│   ├── generate-catalog.py
│
└── .github/
    └── workflows/
        └── taxonomy.yml
```

---

## Taxonomy Model

Each repository is classified using:

### Domains

Examples:

* ai
* security
* networking
* linux
* windows
* macos
* homelab
* github
* virtualization
* education
* mathematics
* audio

### Technologies

Examples:

* python
* powershell
* typescript
* nodejs
* go
* rust
* docker
* qemu
* nginx
* hyprland
* nixos
* wsl2

### Kinds

Examples:

* cli
* guide
* automation
* research
* monitoring
* hardening
* toolkit

---

## Workflow

### 1. Collect repositories

```bash
python scripts/collect-repos.py
```

### 2. Generate taxonomy

```bash
python scripts/generate-taxonomy.py
```

### 3. Validate

```bash
python scripts/validate-taxonomy.py
```

### 4. Apply topics

```bash
python scripts/apply-topics.py
```

### 5. Generate catalog

```bash
python scripts/generate-catalog.py
```

---

## Governance Rules

* Maximum 8 GitHub topics per repository.
* At least 1 domain required.
* Forks are excluded from KPI calculations.
* Private repositories are included in local reports.
* Unclassified repositories must be reviewed manually.

---

## Generated Artifacts

### inventory/repos.json

Raw inventory from GitHub.

### inventory/portfolio.json

Normalized repository metadata.

### inventory/topics.tsv

Generated GitHub topics.

### reports/statistics.md

Portfolio metrics.

### reports/unclassified.md

Repositories requiring manual review.

### reports/stale.md

Repositories not updated recently.

---

## License

MIT
