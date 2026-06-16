#!/usr/bin/env python3

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INVENTORY_DIR = ROOT / "inventory"

OUTPUT_FILE = INVENTORY_DIR / "repos.json"

OWNER = "valorisa"


def run_gh() -> list[dict]:
    cmd = [
        "gh",
        "repo",
        "list",
        OWNER,
        "--limit",
        "500",
        "--json",
        ",".join(
            [
                "name",
                "description",
                "isFork",
                "isPrivate",
                "updatedAt",
                "url",
            ]
        ),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)

    return json.loads(result.stdout)


def main() -> None:
    INVENTORY_DIR.mkdir(exist_ok=True)

    repos = run_gh()

    OUTPUT_FILE.write_text(
        json.dumps(repos, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"[OK] {len(repos)} repositories collected")
    print(f"[OK] Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
    