# Spec 001 — Push-to-talk dictation (baseline)

**Status:** Implemented (reverse-engineered from working code, 2026-09).
Motivated by [../../docs/prd.md](../../docs/prd.md); constrained by
[../constitution.md](../constitution.md).

Verification column: **auto** = pytest in `tests/001-push-to-talk-dictation/`;
**manual** = checklist entry in [manual-tests.md](manual-tests.md) (OS integration —
real permissions, hardware, or login items that cannot be automated).

| REQ | Requirement (acceptance criterion) | Verification |
|---|---|---|
| REQ-001 | Holding Right Option starts recording and plays the Tink sound | manual |
| REQ-002 | Releasing Right Option stops recording, plays Pop, and triggers transcription | manual |
| REQ-003 | Mic is (re)opened on every press so the current system input device is used | manual |
| REQ-004 | Audio is resampled from the mic's native rate to 16 kHz | auto |
| REQ-005 | Clips shorter than 0.3 s are discarded silently | auto |
| REQ-006 | Clips with RMS below 0.002 are discarded with a diagnostic message | auto |
| REQ-007 | Known hallucination strings ("thank you.", "thanks for watching!", …) are suppressed | auto |
| REQ-008 | Transcribed text + trailing space is pasted into the focused app via Cmd+V | manual |
| REQ-009 | The user's previous clipboard content is restored after pasting | manual |
| REQ-010 | `--list-devices` prints available input devices and exits | auto |
| REQ-011 | `--device <name-or-index>` pins a specific microphone (digits → index, else name substring) | auto |
| REQ-012 | Startup fails with a clear error if the model files are missing | auto |
| REQ-013 | Model is warmed up at startup before "Ready" is printed | manual |
| REQ-014 | Transcription language is English (`en`) | auto |
| REQ-015 | `setup_autostart.sh` installs a hidden-Terminal login item; `--uninstall` removes it | manual |
| REQ-016 | The autostart launcher never starts a second instance if one is running | manual |

## Non-goals (baseline)

- Configurable hotkey, languages other than English, menu-bar UI — candidate future
  specs (002+), each entering at the PRD.

## Downstream

- Design: [plan.md](plan.md)
- Work items: [tasks.md](tasks.md)
- Manual verification: [manual-tests.md](manual-tests.md)
