# ADR-005: Autostart via a Terminal-hosting launcher app (osacompile + login item)

**Status:** Accepted

## Context

The app must start at login and needs Microphone, Input Monitoring, and Accessibility
permissions. macOS grants these per-app; a custom `.app` bundle would need its own
permission grants and cannot reliably inherit them. Admin rights are unavailable.

## Decision

`setup_autostart.sh` compiles an AppleScript launcher (`DictateLauncher.app` via
`osacompile`) and registers it as a login item. At login the launcher tells **Terminal**
(which already holds all required permissions) to run `dictate.py` detached, then hides
the Terminal window.

## Alternatives rejected

- **LaunchAgent (`launchd` plist)** — the spawned process does not inherit Terminal's
  TCC permissions; mic and input monitoring fail.
- **Standalone `.app` bundle running Python directly** — tried and failed (could not
  obtain mic access); the installer still contains cleanup code removing the old
  `Dictate.app` and its TCC entries.

## Consequences

- Terminal must keep running (hidden is fine); quitting Terminal stops dictation until
  relaunched.
- First run requires the user to allow DictateLauncher to control Terminal and System
  Events (Automation permission).
- A `pgrep` guard in the launcher command prevents duplicate instances.
