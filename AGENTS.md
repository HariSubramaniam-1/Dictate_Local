# Agent instructions — Dictation_local

This project is spec-driven (AIDLC). Documents, not code, are the source of truth.
Methodology reference: `Exclude/AIDLC.md`; conversion history: `AIDLC-Dictation_local.md`.

## Before any code change

1. Read [specs/constitution.md](specs/constitution.md) — its 6 invariants are
   non-negotiable without an explicit amendment to that file first.
2. Read the spec that owns the behavior you're touching (baseline:
   [specs/001-push-to-talk-dictation/spec.md](specs/001-push-to-talk-dictation/spec.md)).

## Workflow rules

- **Entry point:** every change enters at the highest affected layer and flows down:
  PRD → architecture/ADR → components → spec → plan → tasks → tests → code.
  New user-visible features get a new `specs/NNN-<feature>/` folder and enter at the PRD.
- **No spec, no code:** nothing lands in `dictate.py` or `setup_autostart.sh` without a
  motivating spec entry. Drift between spec and code is a defect — fix the spec or the
  code, never leave them inconsistent.
- **TDD:** write failing tests from the spec's acceptance criteria before implementing
  (red → green). Every REQ is either covered by pytest in `tests/` or tagged *manual*
  with a checklist entry in the feature's `manual-tests.md`.
- **One fact, one layer:** don't restate facts across documents; reference the layer
  that owns them (e.g., constants live in `dictate.py`, listed in plan 001).

## Verification

- Automated: `python3 -m pytest tests/` (conftest stubs mic/model deps; only
  `numpy` + `pytest` needed).
- Sanity: `python3 dictate.py --list-devices` must still work after any refactor.
- OS-level REQs: run the checklist in
  [specs/001-push-to-talk-dictation/manual-tests.md](specs/001-push-to-talk-dictation/manual-tests.md)
  before marking a spec change implemented.

## Artifact map

| Layer | Location |
|---|---|
| PRD | [docs/prd.md](docs/prd.md) |
| Architecture (HLD) | [docs/architecture.md](docs/architecture.md) |
| Decisions | [docs/adr/](docs/adr/) (ADR-001…006) |
| Components | [docs/components.md](docs/components.md) |
| Constitution | [specs/constitution.md](specs/constitution.md) |
| Feature specs | `specs/NNN-<feature>/{spec,plan,tasks,manual-tests}.md` |
| Automated tests | `tests/NNN-<feature>/` |
| Code | `dictate.py`, `setup_autostart.sh` |
