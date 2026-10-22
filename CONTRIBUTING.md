# Branching & Releases

## Branches

```
main ──●──●──●───────●──●──────────●──▶   (immer releasefaehig, nur per PR)
        \             \            ↑ merge zurueck (fixes)
         feature/x     release/1.2 ●──●──●──▶   (Release Candidates, nur fixes)
                                  v1.2.0rc1  v1.2.0rc2 = v1.2.0
```

| Branch | Zweck | Regeln (Rulesets) |
|---|---|---|
| `main` | Integrationszweig | kein Push/Force-Push/Loeschen, PR mit 1 Review (Code Owner), Checks `ci-ok` + `security-ok` + CodeQL ohne High-Alerts, Branch muss aktuell sein |
| `release/X.Y` | Release Candidates einer Minor-Version | wie `main`; anlegen nur durch Admins; nur PRs von `fix/*`, `hotfix/*`, `deps/*` |
| `feature/*`, `fix/*`, `hotfix/*`, `chore/*`, `docs/*`, `refactor/*`, `ci/*`, `deps/*` | Arbeitszweige | Namensschema wird in der CI (`branch-policy`) erzwungen |
| Tags `v*` | Releases | anlegen/aendern/loeschen nur durch Admins |

Admins duerfen die Review-Pflicht **nur ueber einen PR** umgehen (Solo-Betrieb);
direkte Pushes bleiben auch fuer sie gesperrt.

## Ablauf

1. **Feature**: `git switch -c feature/suche-filter main` → PR nach `main`.
2. **Release-Candidate starten** (Admin):
   ```bash
   git switch -c release/1.2 origin/main && git push -u origin release/1.2
   git tag -a v1.2.0rc1 -m "Bildfinder 1.2.0rc1" && git push origin v1.2.0rc1
   ```
   → `release.yml` baut ein **Pre-Release** mit Exe.

   **Ohne lokales Git:** Actions → *Release taggen* → *Run workflow* → Tag eingeben
   (z.B. `v1.2.0rc1`). Der Workflow taggt die Spitze von `release/1.2` und startet
   die Release-Pipeline. (Das Tag-Ruleset erlaubt dafuer GitHub Actions als Ausnahme.)
3. **Fehler im RC**: `fix/*` von `release/1.2`, PR nach `release/1.2`, danach
   `release/1.2` per PR nach `main` zurueckmergen. Neuer Tag `v1.2.0rc2`.
4. **Finales Release**: den getesteten RC-Commit erneut taggen:
   ```bash
   git tag -a v1.2.0 -m "Bildfinder 1.2.0" v1.2.0rc2 && git push origin v1.2.0
   ```
   Die Pipeline lehnt finale Tags ab, die nicht auf einem RC-Commit von
   `release/1.2` liegen.
5. **Hotfix** 1.2.1: `hotfix/*` → PR nach `release/1.2` → `v1.2.1rc1` → `v1.2.1`.

Versionen folgen PEP 440 (`1.2.0rc1`), die Paketversion wird aus dem Tag abgeleitet.

## Vor jedem PR

```bash
uv run poe fmt && uv run poe check
```
