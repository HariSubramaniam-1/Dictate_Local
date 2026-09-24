# ADR-002: pynput for the global hotkey

**Status:** Accepted

## Context

The app needs a global push-to-talk hotkey (Right Option) that works regardless of
which application has focus, without admin rights or extra installed software.

## Decision

Use `pynput`'s keyboard listener for global press/release detection of Right Option.

## Alternatives rejected

- **Karabiner-Elements / native helper app** — requires a separate install (and in
  Karabiner's case a kernel/system extension), conflicting with the no-extra-installs
  constraint.

## Consequences

- Pure-Python dependency; only requires the **Input Monitoring** permission for the
  hosting Terminal.
- The same library provides `keyboard.Controller` for simulating Cmd+V
  ([ADR-004](ADR-004-clipboard-paste.md)).
