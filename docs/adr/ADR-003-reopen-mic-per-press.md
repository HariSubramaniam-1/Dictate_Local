# ADR-003: Reopen the mic and reinitialize PortAudio on every key press

**Status:** Accepted

## Context

Users switch between AirPods, the built-in mic, and USB mics mid-session. PortAudio
caches its device list at initialization, so a long-lived input stream (or even a
long-lived PortAudio session) goes stale when the system default input changes.

## Decision

On every hotkey press: terminate and reinitialize PortAudio (`sd._terminate()` /
`sd._initialize()`), query the current default (or pinned) input device, and open a
fresh `InputStream` at the device's native sample rate. The stream is closed on release.

## Alternatives rejected

- **Long-lived stream opened at startup** — does not follow device switches; recording
  silently continues from a disconnected or non-default device.

## Consequences

- Device switches (AirPods ↔ built-in) are always picked up on the next press.
- Stream opening happens on a daemon thread so the hotkey stays responsive; a race
  (key released before the stream finishes opening) must be handled — see the plan of
  spec 001.
- Uses private `sounddevice` API (`_terminate`/`_initialize`); acceptable for a
  single-user tool, revisit if `sounddevice` changes.
