# ADR-001: mlx-whisper with whisper-large-v3-turbo from local disk

**Status:** Accepted

## Context

Transcription must run fully offline on an Apple Silicon Mac (PRD constraint: audio
never leaves the device), with good accuracy and latency of a few seconds for short
utterances, inside a plain Python process without admin rights.

## Decision

Use `mlx-whisper` with the `mlx-community/whisper-large-v3-turbo` model, loaded from
local disk (`models/config.json` + `models/weights.safetensors`, downloaded once via
browser because corporate SSL inspection blocks Python's Hugging Face download).

## Alternatives rejected

- **Cloud STT (Whisper API, WisprFlow, etc.)** — violates the offline constraint;
  audio would leave the device.
- **whisper.cpp** — works offline, but requires a compiled binary and bindings;
  MLX is simpler to integrate in pure Python and uses the Apple GPU directly.

## Consequences

- ~1.6 GB of model weights on disk; ~3 GB RAM while running.
- Inference runs on the M-series GPU via MLX; warm-up at startup avoids first-use lag.
- Whisper hallucinates on silence — mitigated by [ADR-006](ADR-006-silence-gate.md).
