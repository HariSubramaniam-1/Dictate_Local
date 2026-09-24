# Tasks 001 — Push-to-talk dictation

Baseline decomposition. All tasks **done** (system was built before this spec was
extracted); kept for traceability. Design detail in [plan.md](plan.md).

| # | Task | Traces to | Status |
|---|---|---|---|
| 1 | Hotkey listener with press/release handlers | REQ-001, REQ-002 | done |
| 2 | Per-press stream open with PortAudio refresh | REQ-003 | done |
| 3 | Audio callback + frame accumulation under lock | REQ-001 | done |
| 4 | Resampler | REQ-004 | done |
| 5 | Duration + silence gates | REQ-005, REQ-006 | done |
| 6 | Transcription call with hallucination filter | REQ-007, REQ-014 | done |
| 7 | Paste with clipboard restore | REQ-008, REQ-009 | done |
| 8 | CLI (`--list-devices`, `--device`) | REQ-010, REQ-011 | done |
| 9 | Model presence check + warm-up | REQ-012, REQ-013 | done |
| 10 | Autostart installer/uninstaller | REQ-015, REQ-016 | done |
| 11 | Testability refactor: extract pure gate/filter/CLI functions from `finish()`/`main()` (behavior-preserving) | REQ-004..007, REQ-010..012 | done |
| 12 | Automated tests in `tests/001-push-to-talk-dictation/` | REQ-004..007, REQ-010..012, REQ-014 | done |
| 13 | Manual test checklist ([manual-tests.md](manual-tests.md)) | REQ-001..003, REQ-008/009, REQ-013, REQ-015/016 | done |
