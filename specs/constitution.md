# Constitution — Dictation_local

Never-break invariants. Any change that would violate one of these requires an explicit
amendment to this file first.

1. **Offline-only at runtime.** No network access after install; audio never leaves the
   machine.
2. **Push-to-talk UX.** Hold key → speak → release → text appears in the focused app.
3. **Single-file application.** `dictate.py` stays one file; no package structure
   without a constitution amendment.
4. **No admin rights.** Everything installs under the user's home folder.
5. **Device resilience.** Mic switching (AirPods ↔ built-in) must always work.
6. **Fail silent, not wrong.** When in doubt (silence, hallucination), output nothing.

## Process rules

- No change lands in `dictate.py` or `setup_autostart.sh` without a spec entry that
  motivates it. Drift between spec and code is a defect.
- Every change enters at the highest affected layer (PRD → architecture/ADR →
  components → spec → plan → tasks → tests → code) and flows downward.
- Every REQ has an executable acceptance test in `tests/`, or is tagged *manual* with
  justification and a checklist entry in the feature's `manual-tests.md`.
