# Local Dictation (WisprFlow alternative)

Push-to-talk speech-to-text for macOS on Apple Silicon. **Fully offline.** Audio never leaves the machine.

**Hold Right Option → speak → release → the text is pasted into whatever app has focus.**

---

## Project docs (spec-driven)

This project follows the AIDLC spec-driven workflow (see `AGENTS.md` for the rules):

- `docs/` — PRD, architecture, ADRs, component breakdown
- `specs/` — constitution (invariants) and feature specs with REQ-IDs
- `tests/` — automated acceptance tests (`python3 -m pytest tests/`)

---

## Requirements

| Category | Requirement |
|---|---|
| Hardware | Apple Silicon Mac (M1/M2/M3/M4); built on an **M3 MacBook Pro** |
| OS | macOS with Privacy & Security permission controls (Sonoma/Sequoia or later) |
| Python | Python 3.10+, native arm64 (built with python.org **Python 3.14**) |
| Python packages | `mlx-whisper`, `sounddevice`, `numpy`, `pynput` |
| Model | `mlx-community/whisper-large-v3-turbo`: `config.json` + `weights.safetensors` (~1.6 GB) |
| Disk | ~2 GB free (model + Python environment) |
| Memory | ~3 GB RAM while running |
| Network | Only for the one-time package install and model download; **none at runtime** |
| Permissions (Terminal) | Microphone, Input Monitoring, Accessibility |
| Permissions (DictateLauncher) | Automation → control Terminal and System Events (for autostart) |
| Admin rights | Not required; installs in your user folders only |
| Microphone | Any macOS input device (built-in, AirPods, USB) |

---

## How it works

```
Hold ⌥ (right) ──► mic opens ──► release ⌥ ──► Whisper (on-device, MLX/GPU) ──► clipboard ──► Cmd+V
     Tink 🔔                         Pop 🔔
```

| Stage | Component | Notes |
|---|---|---|
| Hotkey | `pynput` keyboard listener | Right Option key; needs **Input Monitoring** |
| Record | `sounddevice` (PortAudio) | Mic reopened on every press, so AirPods ↔ built-in switching works |
| Resample | NumPy | Mic's native rate (48 kHz / 24 kHz) → 16 kHz for Whisper |
| Silence gate | RMS check | Skips silent clips, which stops Whisper's "Thank you" hallucination |
| Transcribe | `mlx-whisper` + `whisper-large-v3-turbo` | Runs on the M3 GPU; model loaded from local disk |
| Output | `pbcopy` + simulated Cmd+V | Restores your previous clipboard; needs **Accessibility** |

---

## File structure

```
~/Documents/Dictation_local/
├── dictate.py              # the dictation app
├── setup_autostart.sh      # installs/removes start-at-login
└── models/                 # Whisper model (downloaded manually)
    ├── config.json
    └── weights.safetensors # ~1.6 GB

~/dictate-env/                          # Python virtual environment
~/Applications/DictateLauncher.app      # login item created by setup_autostart.sh
~/Library/Logs/dictate.log              # runtime log
```

---

## Setup (one-time)

### 1. Python environment
```bash
python3 -m venv ~/dictate-env
source ~/dictate-env/bin/activate
pip install mlx-whisper sounddevice numpy pynput
```

### 2. Whisper model (manual download)
The corporate network blocks Python's download from Hugging Face (SSL inspection), so download the model in the browser instead:

1. Open `huggingface.co/mlx-community/whisper-large-v3-turbo` → **Files and versions**
2. Download `config.json` and `weights.safetensors`
3. Place both in `Dictation_local/models/`

### 3. macOS permissions for **Terminal**
System Settings → Privacy & Security:

| Permission | Why |
|---|---|
| Microphone | Record voice |
| Input Monitoring | Detect the Right Option hotkey |
| Accessibility | Send Cmd+V to paste |

After changing any of these, fully quit Terminal (**Cmd+Q**) and reopen it.

### 4. Start at login
```bash
cd ~/Documents/Dictation_local
bash setup_autostart.sh
```
- On the first run, allow **DictateLauncher** to control **Terminal** and **System Events**.
- It adds `DictateLauncher.app` to Login Items and starts dictation right away.
- At login, DictateLauncher starts `dictate.py` through Terminal and then hides Terminal.

---

## Daily use

| Action | Command |
|---|---|
| Dictate | Hold **Right Option**, speak, release |
| Check status/log | `tail -f ~/Library/Logs/dictate.log` |
| Is it running? | `pgrep -fl dictate.py` |
| Stop | `pkill -f dictate.py` |
| Start | `open ~/Applications/DictateLauncher.app` |
| Run in foreground (debug) | `source ~/dictate-env/bin/activate && python3 dictate.py` |
| List microphones | `python3 dictate.py --list-devices` |
| Force a specific mic | `python3 dictate.py --device "MacBook Pro"` |
| Uninstall autostart | `bash setup_autostart.sh --uninstall` |

> Keep Terminal running (hidden is fine). If you quit Terminal, run the **Start** command again.

### Reading the log
| Log line | Meaning |
|---|---|
| `Ready. Hold RIGHT OPTION...` | Model loaded, listening |
| `Mic: MacBook Pro Microphone @ 48000 Hz` | Mic opened for this press |
| `[0.8s, level 0.0300] your text` | Success: transcription time and audio level |
| `Silent audio (level 0.00000)` | Mic permission denied, or mic muted |
| `No audio captured` | Mic stream failed to open |

---

## Configuration (`dictate.py`)

| Setting | Default | Purpose |
|---|---|---|
| `HOTKEY` | `keyboard.Key.alt_r` | Push-to-talk key |
| `LANGUAGE` | `"en"` | Transcription language |
| `MODEL` | `./models` | Local model folder |
| `MIN_SECONDS` | `0.3` | Ignore accidental taps |
| `SILENCE_RMS` | `0.002` | Silence threshold |
| `HALLUCINATIONS` | `{"thank you", ...}` | Outputs that are never pasted |

---

## Troubleshooting (issues hit during the build)

| Symptom | Cause | Fix |
|---|---|---|
| `HFValidationError: Repo id must be...` | Model folder not found at the configured path | Put the files in `./models/` next to `dictate.py` |
| `PaMacCore ... err='-50'` | Mic doesn't support 16 kHz | Fixed: records at the native rate and resamples |
| `This process is not trusted!` | Accessibility / Input Monitoring missing | Grant both to Terminal, then Cmd+Q and reopen |
| No Tink sound | Input Monitoring not active | Check with `python3 -c "import Quartz; print(Quartz.CGPreflightListenEventAccess())"`; it should print `True` |
| Everything transcribes as "Thank you" | Whisper receiving silence | Fixed: silence gate; check Mic permission |
| Stops working after switching AirPods ↔ built-in | Mic stream bound at startup | Fixed: mic reopened on every press |
| `incompatible architecture (have 'arm64', need 'x86_64')` | App launched under Rosetta | Avoided by the Terminal-based launcher |
| Silent audio when run as a standalone `.app` | python.org Python is signed with hardened runtime and lacks the mic entitlement, so macOS denies without prompting | **Design decision:** run through Terminal, which already has mic access (`DictateLauncher`) |

---

## Design notes

- **Offline by design:** no cloud APIs. The model loads from local disk, which suits data-handling constraints.
- **Why Terminal-hosted:** macOS assigns permissions to the "responsible" app. A custom `.app` wrapping python.org's Python can't get microphone access without re-signing Python, while Terminal already holds all three permissions.

## Possible next steps
- Menu-bar icon (status, recording indicator, Quit)
- Custom vocabulary via Whisper's `initial_prompt`
- Smaller model (`small`/`base`) for lower latency
- Optional local LLM cleanup (Ollama) for punctuation and formatting
