# Contributing

## Workflow
- Small PRs, clear scope, tests where reasonable.
- Commit style: **Conventional Commits** (e.g., `feat: add funding window alerts`).
- Releases follow **Semantic Versioning**; update **CHANGELOG.md**.

## Code style
- Python ≥3.12, type hints, `ruff` or `flake8` + `black`.

## Docs
- Add/Update ADRs for notable choices (`docs/ADR-XXXX-*.md`).

## Synchronization Policy
**IMPORTANT:** All changes must be synchronized across Local, VPS, and GitHub before ending any work session. No environment should diverge from the others.

### Before ending work:
1. Commit all changes locally
2. Push to GitHub (`git push origin main`)
3. Pull on VPS (`git pull origin main`)
4. Verify all environments are in sync
