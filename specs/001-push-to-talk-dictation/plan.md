# Plan 001 — Push-to-talk dictation

Low-level design for [spec.md](spec.md). Architecture context:
[../../docs/architecture.md](../../docs/architecture.md); decisions in
[../../docs/adr/](../../docs/adr/).

## Threading and race handling (ADR-003)

- Main thread runs the `pynput` keyboard listener.
- Press: clear frame buffer, set `recording = True`, spawn a daemon thread running
  `start_stream()`.
- The PortAudio callback thread appends frames under `frames_lock` only while
  `recording` is true.
- Stream lifecycle (open/stop/close, the `stream` global) is guarded by `stream_lock`.
- Release: set `recording = False`, spawn a daemon thread running `finish()`.
- **Race:** if the key is released before the stream finishes opening, `start_stream`
  detects `recording == False` after opening and stops/closes the fresh stream
  immediately instead of publishing it.

## Capture and resampling (REQ-003, REQ-004)

- Per press: `sd._terminate()` + `sd._initialize()` refresh PortAudio's device list,
  then the default (or pinned) input device is queried and opened at its
  `default_samplerate` (mono float32).
- `resample(audio, src_rate)` converts to 16 kHz via `np.interp` linear interpolation;
  same-rate input is returned unchanged.

## Gating (REQ-005, REQ-006, REQ-007 — ADR-006)

Pure, unit-testable functions (extracted from `finish()` so tests need no microphone):

- `should_transcribe(audio) -> (ok, reason, rms)`: too-short clips fail with no
  message; sub-RMS clips fail with a diagnostic message; otherwise ok with measured RMS.
- `is_hallucination(text) -> bool`: case-insensitive membership in `HALLUCINATIONS`.

`finish()` orchestrates: stop stream → swap out frame buffer → resample → gate →
transcribe (`mlx_whisper.transcribe`, `language="en"`,
`condition_on_previous_text=False`) → hallucination filter → paste. Tests stub
`dictate.mlx_whisper.transcribe`.

## Output path (REQ-008, REQ-009 — ADR-004)

`pbpaste` capture → `pbcopy` transcript → simulated Cmd+V via `keyboard.Controller` →
0.3 s delay → `pbcopy` restore of previous content. A trailing space is appended to the
transcript.

## CLI and startup (REQ-010..014)

- `build_parser()` defines `--list-devices` (print `sd.query_devices()`, return) and
  `--device` (string).
- `parse_device(value)`: digits → `int` index, otherwise name substring.
- `ensure_model(model_dir)`: exits with a clear error if `config.json` is absent
  (REQ-012).
- Warm-up: one transcription of 1 s of zeros before printing "Ready" (REQ-013).

## Autostart (REQ-015, REQ-016 — ADR-005)

`setup_autostart.sh`: compiles an AppleScript launcher via `osacompile`, registers it
as a login item, and starts it. The launcher's shell command has a
`pgrep -f dictate.py` guard so a running instance is never duplicated. `--uninstall`
removes the login item and launcher app. Legacy `Dictate.app` cleanup runs on every
invocation.

## Constants (single source of truth: `dictate.py`)

| Constant | Value | REQ |
|---|---|---|
| `HOTKEY` | Right Option (`alt_r`) | REQ-001/002 |
| `WHISPER_RATE` | 16000 Hz | REQ-004 |
| `MIN_SECONDS` | 0.3 | REQ-005 |
| `SILENCE_RMS` | 0.002 | REQ-006 |
| `LANGUAGE` | `"en"` | REQ-014 |
| `HALLUCINATIONS` | see `dictate.py` | REQ-007 |
