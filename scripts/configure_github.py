"""Setzt Sicherheitseinstellungen und Branch-/Tag-Rulesets des GitHub-Repos.

Benoetigt ein Token mit Admin-Rechten auf dem Repo (classic PAT ``repo`` oder
fine-grained PAT mit "Administration: write"):

    GITHUB_TOKEN=... uv run poe configure-github --repo owner/name [--dry-run]

Das Skript ist idempotent: vorhandene Rulesets gleichen Namens werden aktualisiert.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API = "https://api.github.com"
RULESETS_DIR = Path(__file__).resolve().parent.parent / ".github" / "rulesets"

REPO_SETTINGS: dict[str, Any] = {
    "allow_squash_merge": True,
    "allow_merge_commit": True,
    "allow_rebase_merge": False,
    "allow_auto_merge": True,
    "delete_branch_on_merge": True,
    "allow_update_branch": True,
    "squash_merge_commit_title": "PR_TITLE",
    "squash_merge_commit_message": "PR_BODY",
    "security_and_analysis": {
        "secret_scanning": {"status": "enabled"},
        "secret_scanning_push_protection": {"status": "enabled"},
    },
}

# Nur GitHub-eigene, verifizierte und diese explizit vertrauten Actions zulassen.
ALLOWED_ACTION_PATTERNS = ["astral-sh/*", "gitleaks/*", "google/*", "ossf/*"]


class GitHub:
    def __init__(self, token: str, repo: str, dry_run: bool) -> None:
        self.token = token
        self.repo = repo
        self.dry_run = dry_run

    def call(self, method: str, path: str, body: Any = None) -> Any:
        url = f"{API}/repos/{self.repo}{path}"
        if self.dry_run and method != "GET":
            print(f"[dry-run] {method} {url}\n{json.dumps(body, indent=2) if body else ''}")
            return None
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(url, data=data, method=method)  # noqa: S310
        request.add_header("Authorization", f"Bearer {self.token}")
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310  # nosec B310
            payload = response.read()
        return json.loads(payload) if payload else None


def step(name: str, func: Any, *args: Any) -> bool:
    try:
        func(*args)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        print(f"  FEHLER  {name}: HTTP {exc.code} {detail}")
        return False
    print(f"  ok      {name}")
    return True


def apply_rulesets(gh: GitHub) -> None:
    try:
        existing = {r["name"]: r["id"] for r in gh.call("GET", "/rulesets") or []}
    except urllib.error.HTTPError as exc:
        print(f"  FEHLER  Rulesets lesen: HTTP {exc.code}")
        return
    for file in sorted(RULESETS_DIR.glob("*.json")):
        ruleset = json.loads(file.read_text(encoding="utf-8"))
        name = ruleset["name"]
        if name in existing:
            step(
                f"Ruleset aktualisieren: {name}",
                gh.call,
                "PUT",
                f"/rulesets/{existing[name]}",
                ruleset,
            )
        else:
            step(f"Ruleset anlegen: {name}", gh.call, "POST", "/rulesets", ruleset)


def configure_release_environment(gh: GitHub) -> bool:
    """Environment 'release' darf nur von v*-Tags aus deployen (Release-Workflow)."""
    env_body = {
        "deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True}
    }
    ok = step("Environment 'release' anlegen", gh.call, "PUT", "/environments/release", env_body)
    if not ok or gh.dry_run:
        return ok
    policies_path = "/environments/release/deployment-branch-policies"
    policies = gh.call("GET", policies_path) or {}
    if any(p["name"] == "v*" for p in policies.get("branch_policies", [])):
        print("  ok      Environment 'release': Tag-Regel v* vorhanden")
        return True
    return step(
        "Environment 'release': nur Tags v*",
        gh.call,
        "POST",
        policies_path,
        {"name": "v*", "type": "tag"},
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"), help="owner/name")
    parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, nichts aendern")
    args = parser.parse_args(argv)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not args.repo or not token:
        print("--repo und GITHUB_TOKEN (Admin-Token) werden benoetigt.", file=sys.stderr)
        return 2

    gh = GitHub(token, args.repo, args.dry_run)
    print(f"Konfiguriere {args.repo}")
    results = [
        step(
            "Repo-Einstellungen + Secret Scanning/Push Protection",
            gh.call,
            "PATCH",
            "",
            REPO_SETTINGS,
        ),
        step("Dependabot Alerts", gh.call, "PUT", "/vulnerability-alerts"),
        step("Dependabot Security Updates", gh.call, "PUT", "/automated-security-fixes"),
        step("Private Vulnerability Reporting", gh.call, "PUT", "/private-vulnerability-reporting"),
        step(
            "Workflow-Token nur lesend, keine PR-Approvals durch Actions",
            gh.call,
            "PUT",
            "/actions/permissions/workflow",
            {"default_workflow_permissions": "read", "can_approve_pull_request_reviews": False},
        ),
        step(
            "Nur ausgewaehlte Actions erlauben",
            gh.call,
            "PUT",
            "/actions/permissions",
            {"enabled": True, "allowed_actions": "selected"},
        ),
        step(
            "Erlaubte Actions",
            gh.call,
            "PUT",
            "/actions/permissions/selected-actions",
            {
                "github_owned_allowed": True,
                "verified_allowed": True,
                "patterns_allowed": ALLOWED_ACTION_PATTERNS,
            },
        ),
    ]
    results.append(configure_release_environment(gh))
    apply_rulesets(gh)
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
