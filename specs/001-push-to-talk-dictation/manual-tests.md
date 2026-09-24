# Manual tests 001 — Push-to-talk dictation

OS-integration checks that cannot be automated (real permissions, hardware, login
items). Run this checklist before marking any change to spec 001 as implemented.

Last full run: 2026-09-24 — all passed.

| REQ | Why manual | Checklist step | Pass |
|---|---|---|---|
| REQ-001 | Global hotkey needs real Input Monitoring permission | Hold Right Option → Tink heard, recording starts | ☑ |
| REQ-002 | Same | Release Right Option → Pop heard, transcription runs | ☑ |
| REQ-003 | Real device switching | Switch to AirPods mid-session → next press logs the AirPods mic | ☑ |
| REQ-008 | Simulated Cmd+V into a real focused app | Dictate into TextEdit → text + trailing space appears at the cursor | ☑ |
| REQ-009 | Real clipboard round-trip | Copy some text first, dictate, then Cmd+V → the originally copied text is pasted | ☑ |
| REQ-013 | Timing observation | Start `dictate.py` → "Ready" appears only after the warm-up completes | ☑ |
| REQ-015 | Login items + AppleScript | `bash setup_autostart.sh`, reboot → `~/Library/Logs/dictate.log` shows "Ready"; `--uninstall` removes the login item | ☑ |
| REQ-016 | Process-level guard | With dictation running, `open ~/Applications/DictateLauncher.app` again → `pgrep -fl dictate.py` shows exactly one instance | ☑ |
