# Architecture (HLD) — Dictation_local

Satisfies [prd.md](prd.md). Decisions behind each choice are recorded in [adr/](adr/).

## Pipeline

```
hotkey listener ──► mic capture ──► resample to 16 kHz ──► silence gate ──► Whisper (MLX, on-device GPU) ──► clipboard paste with restore
 (Right Option)      (per-press          (NumPy)             (RMS + duration       (whisper-large-v3-turbo          (pbcopy + Cmd+V,
                      fresh stream)                           + blocklist)          from local disk)                 previous clipboard restored)
```

Audio feedback: Tink sound on press (recording started), Pop on release (recording stopped).

## Tech stack

| Layer | Choice | ADR |
|---|---|---|
| Language/runtime | Python 3.10+ native arm64, single process | — |
| Transcription | `mlx-whisper` + `whisper-large-v3-turbo` (local weights) | [ADR-001](adr/ADR-001-mlx-whisper-local-model.md) |
| Hotkey | `pynput` global keyboard listener | [ADR-002](adr/ADR-002-pynput-hotkey.md) |
| Audio capture | `sounddevice` (PortAudio), stream reopened per press | [ADR-003](adr/ADR-003-reopen-mic-per-press.md) |
| Resampling | `numpy` linear interpolation | — |
| Output | `pbcopy`/`pbpaste` + simulated Cmd+V | [ADR-004](adr/ADR-004-clipboard-paste.md) |
| Autostart | Terminal-hosting launcher app via `osacompile` | [ADR-005](adr/ADR-005-terminal-autostart.md) |
| Silence handling | RMS gate + min duration + hallucination blocklist | [ADR-006](adr/ADR-006-silence-gate.md) |
| System tools | `afplay` (sounds), `pbcopy`/`pbpaste` (clipboard), AppleScript/`osacompile` | — |

## Runtime topology

Single process, four thread roles:

| Thread | Role |
|---|---|
| Main | `pynput` keyboard listener (blocks on `listener.join()`) |
| Daemon per press | Opens the mic stream (`start_stream`), exits once open |
| PortAudio callback | Appends captured frames to a shared buffer |
| Daemon per release | Stops stream, gates, transcribes, pastes (`finish`) |

Shared state is guarded by two locks: `frames_lock` (frame buffer) and `stream_lock`
(stream lifecycle). Detailed threading and race handling live in the feature plan:
[../specs/001-push-to-talk-dictation/plan.md](../specs/001-push-to-talk-dictation/plan.md).

## Deployment footprint

Everything under the user's home folder (no admin rights):

- `~/Documents/Dictation_local/` — app, installer, model weights
- `~/dictate-env/` — Python virtual environment
- `~/Applications/DictateLauncher.app` — login item (created by `setup_autostart.sh`)
- `~/Library/Logs/dictate.log` — runtime log
