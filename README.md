# Bildfinder

Kleine Desktop-Anwendung (Tkinter), die einen Ordner rekursiv nach Bildern
(`png, jpg, gif, webp, bmp, tif, svg, heic, ico`) durchsucht und die Treffer in
einer Liste anzeigt. Doppelklick oeffnet ein Bild mit dem Standardprogramm.

Das eigentliche Ziel des Repos ist die **Pipeline-Vorlage**: Build, Tests,
Sicherheitschecks, Branching-Regeln und Release-Tagging mit herunterladbarer
`.exe` – alles ueber [uv](https://docs.astral.sh/uv/) gesteuert.

## Download

Fertige Builds liegen unter **Releases** (`bildfinder-<version>-windows-x64.exe`,
plus Linux-Binary, Wheel, sdist und `SHA256SUMS.txt`). Die Herkunft jeder Datei
kann geprueft werden:

```bash
gh attestation verify bildfinder-1.0.0-windows-x64.exe --repo tripledewey-ctrl/template-python
```

## Entwicklung

```bash
uv sync                      # venv + Dev-Abhaengigkeiten (uv.lock)
uv run poe app               # GUI starten
uv run bildfinder --cli ~/Bilder   # Konsolenmodus
uv run poe check             # alles, was die CI auch prueft
```

| Task (`uv run poe <task>`) | Inhalt |
|---|---|
| `fmt` | Code formatieren (ruff) |
| `lint` | ruff-Lint, Format-Check, zizmor (Workflow-Sicherheit) |
| `typecheck` | mypy `--strict` |
| `test` | pytest + Coverage (min. 85 %) |
| `sast` | bandit |
| `audit` | pip-audit gegen `uv.lock` (mit Hashes) |
| `security` | `sast` + `audit` + `lint-workflows` |
| `check` | `lock-check`, `lint`, `typecheck`, `test`, `security` |
| `build` | Wheel + sdist (`uv build`) |
| `build-exe` | Standalone-Exe mit PyInstaller (`uv run --group exe poe build-exe`) |
| `configure-github` | Sicherheitseinstellungen + Rulesets im GitHub-Repo setzen |

Die Version kommt ausschliesslich aus Git-Tags (`hatch-vcs`), es gibt keine
Versionsnummer im Code.

## Pipelines

| Workflow | Ausloeser | Inhalt |
|---|---|---|
| `ci.yml` | PR, Push auf `main`/`release/**` | Branch-Namensregeln, Lint, mypy, Tests (Windows + Linux, Py 3.12/3.13), Wheel + Exe als Artefakt, Pflicht-Check **`ci-ok`** |
| `security.yml` | PR, Push, woechentlich | bandit, pip-audit, zizmor, CodeQL (Python + Actions), OSV-Scanner, gitleaks, Dependency Review, Pflicht-Check **`security-ok`** |
| `scorecard.yml` | Push `main`, woechentlich | OpenSSF Scorecard |
| `release.yml` | Tag `v*` | Tag-/Branch-Pruefung, CI, Exe-Build, SHA256, SLSA-Provenance, GitHub Release |
| `dependabot.yml` | woechentlich | Updates fuer `uv.lock` und Actions (7 Tage Cooldown) |

Alle Actions sind auf Commit-SHAs gepinnt, `GITHUB_TOKEN` ist standardmaessig nur lesend.

Branching- und Release-Ablauf: siehe [CONTRIBUTING.md](CONTRIBUTING.md).
Sicherheitsrichtlinie: siehe [SECURITY.md](SECURITY.md).
