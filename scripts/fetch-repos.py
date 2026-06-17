#!/usr/bin/env python3
"""
fetch-repos.py — Auto-fetch GitHub repositories via REST API.

Usage:
    python scripts/fetch-repos.py [OPTIONS]

Options:
    --user USERNAME         GitHub username (default: env GITHUB_USER or 'valorisa')
    --org ORGNAME           GitHub organization name (mutually exclusive with --user)
    --exclude-forks         Exclude forked repositories
    --exclude-private       Exclude private repositories
    --since YYYY-MM-DD      Only repos updated after this date
    --output PATH           Output file path (default: inventory/repos.json)
    --help                  Show this help message

Environment variables:
    GITHUB_TOKEN            Personal access token (recommended to avoid rate limits)
    GITHUB_USER             Default GitHub username

Examples:
    python scripts/fetch-repos.py
    python scripts/fetch-repos.py --exclude-forks --since 2026-01-01
    python scripts/fetch-repos.py --org my-org --output inventory/org-repos.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("[ERROR] Missing dependency: pip install requests", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GITHUB_API = "https://api.github.com"
PER_PAGE = 100
DEFAULT_OUTPUT = Path("inventory") / "repos.json"
DEFAULT_USER = os.getenv("GITHUB_USER", "valorisa")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_headers(token: str | None) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def check_rate_limit(response: requests.Response) -> None:
    """Warn if rate limit is close to exhaustion."""
    remaining = response.headers.get("X-RateLimit-Remaining")
    if remaining is not None and int(remaining) < 10:
        reset = response.headers.get("X-RateLimit-Reset", "unknown")
        print(
            f"[WARN] GitHub API rate limit almost exhausted "
            f"(remaining: {remaining}, resets at: {reset})",
            file=sys.stderr,
        )


def fetch_page(url: str, headers: dict, params: dict) -> list:
    """Fetch a single page and return the JSON list."""
    response = requests.get(url, headers=headers, params=params, timeout=30)
    check_rate_limit(response)

    if response.status_code == 401:
        print("[ERROR] Invalid or expired GITHUB_TOKEN.", file=sys.stderr)
        sys.exit(1)
    if response.status_code == 403:
        print("[ERROR] API rate limit exceeded. Set GITHUB_TOKEN to increase limits.",
              file=sys.stderr)
        sys.exit(1)
    if response.status_code == 404:
        print(f"[ERROR] Resource not found: {url}", file=sys.stderr)
        sys.exit(1)
    if response.status_code != 200:
        print(f"[ERROR] Unexpected HTTP {response.status_code}: {response.text}",
              file=sys.stderr)
        sys.exit(1)

    return response.json()


def fetch_all_repos(
    target: str,
    is_org: bool,
    headers: dict,
    since: datetime | None,
    exclude_forks: bool,
    exclude_private: bool,
) -> list[dict]:
    """Paginate through all repositories for a user or org."""
    if is_org:
        url = f"{GITHUB_API}/orgs/{target}/repos"
        params_base = {"type": "all", "per_page": PER_PAGE}
    else:
        url = f"{GITHUB_API}/users/{target}/repos"
        params_base = {"type": "all", "per_page": PER_PAGE}

    repos = []
    page = 1

    while True:
        params = {**params_base, "page": page}
        batch = fetch_page(url, headers, params)

        if not batch:
            break

        for repo in batch:
            # Apply filters
            if exclude_forks and repo.get("fork"):
                continue
            if exclude_private and repo.get("private"):
                continue
            if since:
                pushed = repo.get("pushed_at") or repo.get("updated_at")
                if pushed:
                    repo_date = datetime.fromisoformat(
                        pushed.replace("Z", "+00:00")
                    )
                    if repo_date < since:
                        continue

            repos.append({
                "name": repo["name"],
                "description": repo.get("description") or "",
                "isFork": repo.get("fork", False),
                "isPrivate": repo.get("private", False),
                "updatedAt": repo.get("pushed_at"),
                "url": repo.get("html_url"),
                "githubTopics": repo.get("topics", []),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count", 0),
            })

        # Stop if we got fewer results than a full page
        if len(batch) < PER_PAGE:
            break

        page += 1

    return repos


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch GitHub repositories and write inventory/repos.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    target = parser.add_mutually_exclusive_group()
    target.add_argument(
        "--user",
        default=None,
        metavar="USERNAME",
        help=f"GitHub username (default: GITHUB_USER env or '{DEFAULT_USER}')",
    )
    target.add_argument(
        "--org",
        default=None,
        metavar="ORGNAME",
        help="GitHub organization name",
    )
    parser.add_argument(
        "--exclude-forks",
        action="store_true",
        help="Exclude forked repositories",
    )
    parser.add_argument(
        "--exclude-private",
        action="store_true",
        help="Exclude private repositories",
    )
    parser.add_argument(
        "--since",
        default=None,
        metavar="YYYY-MM-DD",
        help="Only include repos updated after this date",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        metavar="PATH",
        help=f"Output file path (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    # Resolve target (user or org)
    is_org = args.org is not None
    target = args.org if is_org else (args.user or DEFAULT_USER)

    # Parse --since date
    since: datetime | None = None
    if args.since:
        try:
            since = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"[ERROR] Invalid date format '{args.since}'. Use YYYY-MM-DD.",
                  file=sys.stderr)
            sys.exit(1)

    # Auth token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print(
            "[WARN] GITHUB_TOKEN not set. Unauthenticated requests are limited "
            "to 60/hour.",
            file=sys.stderr,
        )

    headers = build_headers(token)

    # Fetch
    kind = "org" if is_org else "user"
    print(f"[INFO] Fetching repositories for {kind}: {target}")
    repos = fetch_all_repos(
        target=target,
        is_org=is_org,
        headers=headers,
        since=since,
        exclude_forks=args.exclude_forks,
        exclude_private=args.exclude_private,
    )

    if not repos:
        print("[WARN] No repositories found with the given filters.", file=sys.stderr)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2, ensure_ascii=False)

    # Summary
    forks = sum(1 for r in repos if r["isFork"])
    private = sum(1 for r in repos if r["isPrivate"])
    print(f"[OK] {len(repos)} repositories exported → {output_path}")
    print(f"     Forks   : {forks}")
    print(f"     Private : {private}")
    print(f"     Public  : {len(repos) - private}")
    if since:
        print(f"     Filter  : updated after {args.since}")


if __name__ == "__main__":
    main()
