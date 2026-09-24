# PRD — Dictation_local

## Need

An offline replacement for WisprFlow: system-wide push-to-talk dictation on a corporate
Mac where cloud speech-to-text is not allowed and IT-managed installs are unavailable.

## Users

A single knowledge worker dictating into whatever application currently has focus
(email, editor, chat, browser).

## Business constraints

- Audio must never leave the device — no network access at runtime.
- No admin rights: everything installs under the user's home folder.
- No IT-managed installs or third-party helper apps.
- Must work with the built-in microphone, AirPods, and USB microphones — including
  switching between them mid-session.

## Success measures

| Measure | Target |
|---|---|
| Latency | Transcription completes within a few seconds for short utterances |
| Delivery | Text lands in the currently focused app, cursor position preserved |
| Persistence | Survives reboots (starts at login automatically) |
| Precision | No false output on silence or near-silence (no hallucinated text) |

## Downstream artifacts

- High-level design: [architecture.md](architecture.md)
- Decisions: [adr/](adr/)
- Module breakdown: [components.md](components.md)
- Invariants: [../specs/constitution.md](../specs/constitution.md)
- Baseline feature spec: [../specs/001-push-to-talk-dictation/spec.md](../specs/001-push-to-talk-dictation/spec.md)
