#!/usr/bin/env python3

from __future__ import annotations

import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

INVENTORY_DIR = ROOT / "inventory"
REPORTS_DIR = ROOT / "reports"
TAXONOMY_DIR = ROOT / "taxonomy"

REPOS_FILE = INVENTORY_DIR / "repos.json"
DOMAINS_FILE = TAXONOMY_DIR / "domains.yml"

PORTFOLIO_FILE = INVENTORY_DIR / "portfolio.json"
TOPICS_FILE = INVENTORY_DIR / "topics.tsv"

STATISTICS_FILE = REPORTS_DIR / "statistics.md"
UNCLASSIFIED_FILE = REPORTS_DIR / "unclassified.md"


def load_domains() -> dict:
    if not DOMAINS_FILE.exists():
        raise FileNotFoundError(
            f"Missing taxonomy file: {DOMAINS_FILE}"
        )

    data = yaml.safe_load(
        DOMAINS_FILE.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "domains.yml doit contenir un dictionary"
        )

    return data


def load_repositories() -> list[dict]:
    if not REPOS_FILE.exists():
        raise FileNotFoundError(
            f"Repository inventory not found: {REPOS_FILE}"
        )

    return json.loads(
        REPOS_FILE.read_text(
            encoding="utf-8"
        )
    )


def classify(
    text: str,
    domains: dict,
) -> list[str]:

    text = text.lower()
    found = []

    for domain, config in domains.items():
        keywords = config.get(
            "keywords",
            [],
        )

        if any(
            keyword.lower() in text
            for keyword in keywords
        ):
            found.append(domain)

    return sorted(set(found))


def write_statistics(
    stats: dict,
    classified: int,
    unclassified: int,
) -> None:

    ratio = round(
        (
            classified
            / max(stats["total"], 1)
        )
        * 100,
        2,
    )

    STATISTICS_FILE.write_text(
        "\n".join(
            [
                "# Statistics",
                "",
                f"- Total repositories: {stats['total']}",
                f"- Forks: {stats['forks']}",
                f"- Private: {stats['private']}",
                f"- Classified: {classified}",
                f"- Unclassified: {unclassified}",
                f"- Coverage: {ratio}%",
            ]
        ),
        encoding="utf-8",
    )


def write_unclassified(
    repos: list[str],
) -> None:

    UNCLASSIFIED_FILE.write_text(
        "\n".join(
            [
                "# Unclassified repositories",
                "",
                *[
                    f"- {repo}"
                    for repo in sorted(repos)
                ],
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:

    INVENTORY_DIR.mkdir(
        exist_ok=True
    )

    REPORTS_DIR.mkdir(
        exist_ok=True
    )

    domains = load_domains()
    repos = load_repositories()

    portfolio = []
    unclassified = []

    stats = {
        "total": len(repos),
        "forks": 0,
        "private": 0,
    }

    with TOPICS_FILE.open(
        "w",
        encoding="utf-8",
    ) as topics:

        topics.write(
            "repo\ttopics\n"
        )

        for repo in repos:

            name = repo["name"]

            description = (
                repo.get(
                    "description"
                )
                or ""
            )

            text = (
                f"{name} {description}"
            )

            detected = classify(
                text,
                domains,
            )

            if repo.get(
                "isFork",
                False,
            ):
                stats["forks"] += 1

            if repo.get(
                "isPrivate",
                False,
            ):
                stats["private"] += 1

            if not detected:
                unclassified.append(
                    name
                )

            portfolio.append(
                {
                    "name": name,
                    "topics": detected,
                    "isFork": repo.get(
                        "isFork",
                        False,
                    ),
                    "isPrivate": repo.get(
                        "isPrivate",
                        False,
                    ),
                    "updatedAt": repo.get(
                        "updatedAt"
                    ),
                    "url": repo.get(
                        "url"
                    ),
                }
            )

            topics.write(
                f"{name}\t{','.join(detected)}\n"
            )

    PORTFOLIO_FILE.write_text(
        json.dumps(
            portfolio,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    write_statistics(
        stats,
        classified=(
            len(repos)
            - len(unclassified)
        ),
        unclassified=len(
            unclassified
        ),
    )

    write_unclassified(
        unclassified
    )

    print(
        f"[OK] Portfolio generated ({len(portfolio)} repositories)"
    )

    print(
        f"[OK] Domains loaded: {len(domains)}"
    )

    print(
        f"[OK] Classified: {len(repos) - len(unclassified)}"
    )

    print(
        f"[OK] Unclassified: {len(unclassified)}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(
            f"[ERROR] {exc}"
        )
        sys.exit(1)