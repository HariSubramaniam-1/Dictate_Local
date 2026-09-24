# ADR-006: Silence gate (RMS + duration) and hallucination blocklist

**Status:** Accepted

## Context

Whisper hallucinates plausible text (typically "Thank you.") when given silent or
near-silent audio — e.g. an accidental hotkey tap, a muted mic, or a wrong input
device. The PRD requires no false output on silence, and the constitution mandates
"fail silent, not wrong".

## Decision

Three-layer defense before any text is pasted:

1. **Minimum duration:** clips shorter than 0.3 s are discarded silently.
2. **RMS silence gate:** clips with RMS < 0.002 are discarded with a diagnostic
   message (helps distinguish muted mic / wrong device / missing permission).
3. **Hallucination blocklist:** transcripts matching known hallucination strings
   (case-insensitive: "thank you.", "thank you", "thanks for watching!", "you", ".")
   are suppressed.

## Alternatives rejected

- **No gating (trust Whisper)** — produces false "Thank you." output on every
  accidental tap; violates the precision success measure.

## Consequences

- Very quiet genuine speech below the RMS threshold is dropped; threshold tuning is a
  spec-001 amendment if this becomes a problem.
- The blocklist may suppress a rare legitimate one-word utterance ("you") — accepted
  trade-off for fail-silent behavior.
