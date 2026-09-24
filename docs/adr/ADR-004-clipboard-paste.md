# ADR-004: Paste via pbcopy + simulated Cmd+V, then restore the clipboard

**Status:** Accepted

## Context

Transcribed text must land in whatever app has focus, quickly and reliably, including
Unicode content, without disturbing the user's clipboard.

## Decision

Capture the current clipboard with `pbpaste`, place the transcript on the clipboard
with `pbcopy`, simulate Cmd+V via `pynput`, wait 0.3 s for the paste to complete, then
restore the previous clipboard content.

## Alternatives rejected

- **Typing the text as simulated keystrokes** — slow for long transcripts and
  unreliable with Unicode and non-US keyboard layouts.

## Consequences

- Requires the **Accessibility** permission for the hosting Terminal.
- The user's clipboard is preserved (restored after the 0.3 s paste delay).
- Binary/non-text clipboard content is restored as captured by `pbpaste` (text-level
  fidelity only) — accepted limitation.
