# Sicherheitsrichtlinie

## Schwachstellen melden

Bitte **keine oeffentlichen Issues**. Nutze
[Private Vulnerability Reporting](../../security/advisories/new).
Rueckmeldung innerhalb von 7 Tagen.

## Unterstuetzte Versionen

Nur das jeweils letzte Release (`vX.Y.Z`) erhaelt Sicherheitsupdates.

## Massnahmen im Repo

- Secret Scanning + Push Protection, gitleaks in der CI
- Dependabot Alerts/Security Updates, pip-audit, OSV-Scanner, Dependency Review
- CodeQL (`security-extended`) fuer Python und GitHub Actions, bandit, zizmor
- Gepinnte Actions (SHA), minimal berechtigte `GITHUB_TOKEN`s
- Signierte Build-Provenance (SLSA) und SHA256-Pruefsummen fuer jedes Release
- Rulesets fuer `main`, `release/**` und `v*`-Tags (siehe `.github/rulesets/`)
