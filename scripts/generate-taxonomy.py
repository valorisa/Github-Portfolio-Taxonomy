#!/usr/bin/env python3

from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

REPOS_FILE = ROOT / "inventory" / "repos.json"

if not REPOS_FILE.exists():
    raise FileNotFoundError(
        f"Repository inventory not found: {REPOS_FILE}"
    )

PORTFOLIO_FILE = ROOT / "inventory" / "portfolio.json"

TOPICS_FILE = ROOT / "inventory" / "topics.tsv"

STATISTICS_FILE = ROOT / "reports" / "statistics.md"

UNCLASSIFIED_FILE = ROOT / "reports" / "unclassified.md"


RULES = {
    "ai": [
        "claude",
        "prompt",
        "llm",
        "gemini",
        "qwen",
    ],
    "security": [
        "security",
        "ssh",
        "tls",
        "certificate",
        "password",
        "hardening",
    ],
    "networking": [
        "ntp",
        "vlan",
        "dns",
        "websocket",
        "proxy",
    ],
    "linux": [
        "linux",
        "hyprland",
        "nixos",
        "alpine",
        "kernel",
    ],
    "windows": [
        "windows",
        "powershell",
        "wsl",
    ],
    "macos": [
        "macos",
        "homebrew",
        "swift",
    ],
    "audio": [
        "audio",
        "ffmpeg",
        "loudnorm",
        "podcast",
    ],
    "github": [
        "github",
        "repository",
        "scaffolding",
    ],
    "homelab": [
        "homelab",
        "proxmox",
        "wireguard",
    ],
}


def classify(text: str) -> list[str]:
    text = text.lower()

    found = []

    for topic, keywords in RULES.items():
        if any(keyword in text for keyword in keywords):
            found.append(topic)

    return sorted(set(found))


def main() -> None:

    (ROOT / "inventory").mkdir(exist_ok=True)
    (ROOT / "reports").mkdir(exist_ok=True)
    
    repos = json.loads(
        REPOS_FILE.read_text(encoding="utf-8")
    )

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

        topics.write("repo\ttopics\n")

        for repo in repos:

            name = repo["name"]

            desc = repo.get("description") or ""

            text = f"{name} {desc}"

            detected = classify(text)

            if repo["isFork"]:
                stats["forks"] += 1

            if repo["isPrivate"]:
                stats["private"] += 1

            if not detected:
                unclassified.append(name)

            portfolio.append(
                {
                    "name": name,
                    "topics": detected,
                    "isFork": repo["isFork"],
                    "isPrivate": repo["isPrivate"],
                    "updatedAt": repo["updatedAt"],
                    "url": repo["url"],
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

    STATISTICS_FILE.write_text(
        "\n".join(
            [
                "# Statistics",
                "",
                f"- Total repositories: {stats['total']}",
                f"- Forks: {stats['forks']}",
                f"- Private: {stats['private']}",
            ]
        ),
        encoding="utf-8",
    )

    UNCLASSIFIED_FILE.write_text(
        "\n".join(
            [
                "# Unclassified repositories",
                "",
                *[
                    f"- {repo}"
                    for repo in sorted(unclassified)
                ],
            ]
        ),
        encoding="utf-8",
    )

    print(
        f"[OK] Portfolio generated ({len(portfolio)} repositories)"
    )


if __name__ == "__main__":
    main()
    