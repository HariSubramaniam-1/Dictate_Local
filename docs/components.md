# Component breakdown — Dictation_local

Logical modules of the system. All live in the single file `dictate.py`
(constitution invariant 3) except the autostart installer.

| # | Component | Responsibility | Code today |
|---|---|---|---|
| 1 | Hotkey listener | Detect Right Option press/release globally | `on_press` / `on_release`, `keyboard.Listener` |
| 2 | Audio capture | Open a fresh mic stream per press; accumulate frames | `start_stream`, `stop_stream`, `audio_callback` |
| 3 | Resampler | Mic native rate → 16 kHz (linear interpolation) | `resample` |
| 4 | Silence / hallucination gate | Discard short clips, silent clips, hallucinated text | `should_transcribe`, `is_hallucination` |
| 5 | Transcriber | On-device Whisper inference + startup warm-up | `mlx_whisper.transcribe` call in `finish`, warm-up in `main` |
| 6 | Output (paster) | Paste text via clipboard; restore previous clipboard | `paste` |
| 7 | Audio feedback | Tink on start, Pop on stop | `beep` |
| 8 | CLI | `--list-devices`, `--device <name-or-index>` | `build_parser`, `parse_device`, `main` |
| 9 | Autostart installer | Install/remove hidden-Terminal login item | `setup_autostart.sh` |

Requirement-level behavior of each component:
[../specs/001-push-to-talk-dictation/spec.md](../specs/001-push-to-talk-dictation/spec.md)
