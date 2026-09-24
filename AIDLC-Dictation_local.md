# AIDLC for Dictation_local — Conversion Guide

How to turn **Dictation_local** (offline push-to-talk dictation for macOS on Apple Silicon)
into a spec-driven development project following the AIDLC workflow (see the generic
`AIDLC.md` for the methodology; this document is the project-specific application of it).

---

## 1. Current state

| Asset | Role |
|---|---|
| `dictate.py` | Entire application: hotkey listener, audio capture, resampling, silence gate, Whisper transcription (MLX), clipboard paste |
| `setup_autostart.sh` | Installs/removes a Terminal-based login launcher (`DictateLauncher.app`) |
| `models/` | `whisper-large-v3-turbo` weights (`config.json` + `weights.safetensors`, ~1.6 GB) |
| `README.md` | User-facing setup and usage documentation |

Today, all knowledge lives in the code and README. The goal is to extract it into the
AIDLC artifact stack so future features are spec-driven and the system is regenerable.

## 2. Target repository layout

```
Dictation_local/
├── docs/                                # Phase 0
│   ├── prd.md
│   ├── architecture.md
│   ├── adr/
│   │   ├── ADR-001 ... ADR-006 (see §4)
│   └── components.md
├── specs/                               # Phase 1
│   ├── constitution.md
│   └── 001-push-to-talk-dictation/      # baseline spec (reverse-engineered)
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       └── manual-tests.md              # checklist for REQs that can't be automated
├── tests/
│   └── 001-push-to-talk-dictation/      # automated tests traced to REQ IDs
├── dictate.py
├── setup_autostart.sh
├── models/
└── README.md                            # stays user-facing; links to docs/ and specs/
```

## 3. Phase 0 artifacts — content to write

### docs/prd.md
- **Need:** offline WisprFlow replacement — system-wide dictation on a corporate Mac.
- **Users:** single knowledge worker dictating into any focused app.
- **Business constraints:** audio must never leave the device; no admin rights; no
  IT-managed installs; works with built-in mic, AirPods, and USB mics.
- **Success measures:** transcription latency a few seconds for short utterances;
  text lands in the focused app; survives reboots (autostart); no false output on silence.

### docs/architecture.md (HLD)
- Pipeline: hotkey listener → mic capture → resample to 16 kHz → silence gate →
  Whisper (MLX, on-device GPU) → clipboard paste with restore.
- Tech stack: Python 3.10+ arm64, `pynput`, `sounddevice` (PortAudio), `numpy`,
  `mlx-whisper`; macOS system tools `afplay`, `pbcopy`/`pbpaste`, AppleScript/osacompile.
- Runtime topology: single process, main thread = keyboard listener; stream open and
  transcription each run on daemon threads; shared state guarded by two locks.

### docs/adr/ — decisions to record (reverse-engineered from the code)

| ADR | Decision | Why / rejected alternatives |
|---|---|---|
| ADR-001 | `mlx-whisper` + `whisper-large-v3-turbo` from local disk | On-device GPU inference on Apple Silicon; rejected: cloud STT (violates offline), whisper.cpp (MLX is simpler in Python) |
| ADR-002 | `pynput` for global hotkey (Right Option) | Pure-Python, needs only Input Monitoring; rejected: Karabiner/native helper (extra install) |
| ADR-003 | Reopen mic + reinitialize PortAudio on every key press | Picks up AirPods ↔ built-in device switches; a long-lived stream goes stale on device change |
| ADR-004 | Paste via `pbcopy` + simulated Cmd+V, then restore previous clipboard | Typing keystrokes is slow and unreliable with Unicode; clipboard restore preserves user state |
| ADR-005 | Autostart via Terminal-hosting launcher app (`osacompile` + login item) | .app bundles can't inherit Mic/Accessibility permissions; Terminal already holds them; rejected: LaunchAgent, standalone .app (tried and failed — see cleanup code in `setup_autostart.sh`) |
| ADR-006 | Silence gate (RMS < 0.002) + minimum duration (0.3 s) + hallucination blocklist | Whisper hallucinates "Thank you." on silent/near-silent audio |

### docs/components.md

| Component | Code today |
|---|---|
| Hotkey listener | `on_press` / `on_release`, `keyboard.Listener` |
| Audio capture | `start_stream`, `stop_stream`, `audio_callback` |
| Resampler | `resample` (linear interpolation to 16 kHz) |
| Silence / hallucination gate | RMS + duration checks and blocklist in `finish` |
| Transcriber | `mlx_whisper.transcribe` call + warm-up in `main` |
| Output (paster) | `paste` |
| Audio feedback | `beep` (Tink on start, Pop on stop) |
| CLI | `--list-devices`, `--device` in `main` |
| Autostart installer | `setup_autostart.sh` |

## 4. Phase 1 artifacts

### specs/constitution.md — invariants
1. **Offline-only at runtime.** No network access after install; audio never leaves the machine.
2. **Push-to-talk UX.** Hold key → speak → release → text appears in the focused app.
3. **Single-file application.** `dictate.py` stays one file; no package structure without a constitution amendment.
4. **No admin rights.** Everything installs under the user's home folder.
5. **Device resilience.** Mic switching (AirPods ↔ built-in) must always work.
6. **Fail silent, not wrong.** When in doubt (silence, hallucination), output nothing.

### specs/001-push-to-talk-dictation/spec.md — baseline requirements

| REQ | Requirement (acceptance criterion) |
|---|---|
| REQ-001 | Holding Right Option starts recording and plays the Tink sound |
| REQ-002 | Releasing Right Option stops recording, plays Pop, and triggers transcription |
| REQ-003 | Mic is (re)opened on every press so the current system input device is used |
| REQ-004 | Audio is resampled from the mic's native rate to 16 kHz |
| REQ-005 | Clips shorter than 0.3 s are discarded silently |
| REQ-006 | Clips with RMS below 0.002 are discarded with a diagnostic message |
| REQ-007 | Known hallucination strings ("thank you.", "thanks for watching!", …) are suppressed |
| REQ-008 | Transcribed text + trailing space is pasted into the focused app via Cmd+V |
| REQ-009 | The user's previous clipboard content is restored after pasting |
| REQ-010 | `--list-devices` prints available input devices and exits |
| REQ-011 | `--device <name-or-index>` pins a specific microphone |
| REQ-012 | Startup fails with a clear error if the model files are missing |
| REQ-013 | Model is warmed up at startup before "Ready" is printed |
| REQ-014 | Transcription language is English (`en`) |
| REQ-015 | `setup_autostart.sh` installs a hidden-Terminal login item; `--uninstall` removes it |
| REQ-016 | The autostart launcher never starts a second instance if one is running |

### specs/001-…/plan.md — key design detail (references, not restatements)
- Threading: callback thread appends frames under `frames_lock`; stream lifecycle under
  `stream_lock`; capture and transcription on daemon threads (per ADR-003).
- Race handling: if the key is released before the stream finishes opening, the fresh
  stream is stopped immediately.
- Resampling: `np.interp` linear interpolation (REQ-004); rate read from the device's
  `default_samplerate`.
- Output path: `pbpaste` capture → `pbcopy` → `kb.pressed(cmd)+v` → 0.3 s delay →
  restore (REQ-008/009, ADR-004).
- Autostart: AppleScript compiled via `osacompile`; `pgrep` guard for single instance
  (REQ-015/016, ADR-005).

### specs/001-…/tasks.md — baseline decomposition (all done; kept for traceability)
1. Hotkey listener with press/release handlers → REQ-001, REQ-002
2. Per-press stream open with PortAudio refresh → REQ-003
3. Audio callback + frame accumulation under lock → REQ-001
4. Resampler → REQ-004
5. Duration + silence gates → REQ-005, REQ-006
6. Transcription call with hallucination filter → REQ-007, REQ-014
7. Paste with clipboard restore → REQ-008, REQ-009
8. CLI (`--list-devices`, `--device`) → REQ-010, REQ-011
9. Model presence check + warm-up → REQ-012, REQ-013
10. Autostart installer/uninstaller → REQ-015, REQ-016

## 5. Test strategy (TDD)

Per AIDLC §5, every REQ needs an executable acceptance criterion — or an explicit
*manual* tag with justification. For this project the split is:

### Automated (pure logic — unit-testable with pytest, no hardware)

| REQ | Test approach |
|---|---|
| REQ-004 | `resample()`: feed synthetic sine waves at 48/24 kHz, assert output length and frequency content at 16 kHz |
| REQ-005 | `finish()` with < 0.3 s of frames → no transcription attempted |
| REQ-006 | `finish()` with near-zero-amplitude audio → discarded before transcription |
| REQ-007 | Blocklist filter: "Thank you." → suppressed; normal text → passed through |
| REQ-010/011 | CLI parsing: `--list-devices` exits after printing; `--device 2` → int, `--device MacBook` → string |
| REQ-012 | Missing `models/config.json` → startup exits with the expected error |

Prerequisite refactor (enters at plan level of spec 001): extract the gating logic in
`finish()` into a pure function (audio in → decision out) so it is testable without a
microphone, and inject the transcriber so tests can stub `mlx_whisper.transcribe`.

### Manual checklist (OS integration — automation impossible or not worth it)

| REQ | Why manual | Checklist step |
|---|---|---|
| REQ-001/002 | Global hotkey needs real Input Monitoring permission | Hold/release Right Option → Tink/Pop heard, text pasted |
| REQ-003 | Real device switching | Switch to AirPods mid-session → next press uses AirPods |
| REQ-008/009 | Simulated Cmd+V into a real focused app | Dictate into TextEdit; verify prior clipboard restored |
| REQ-013 | Timing observation | "Ready" appears only after warm-up completes |
| REQ-015/016 | Login items + AppleScript | Install, reboot, check log shows "Ready"; second launch doesn't duplicate |

Layout: automated tests in `tests/001-push-to-talk-dictation/`; the manual checklist
lives in `specs/001-push-to-talk-dictation/manual-tests.md` and is run before marking
any change to spec 001 as implemented.

## 6. Conversion checklist (do in this order)

- [ ] Create `docs/prd.md` from §3
- [ ] Create `docs/architecture.md` from §3
- [ ] Create the six ADRs from §3 (one file each)
- [ ] Create `docs/components.md` from §3
- [ ] Create `specs/constitution.md` from §4
- [ ] Create `specs/001-push-to-talk-dictation/` (spec, plan, tasks) from §4, marked *implemented* — with each REQ's acceptance criterion written as an executable assertion or tagged *manual* per §5
- [ ] Extract pure logic from `finish()` (gating decision, transcriber injection) so it is unit-testable — behavior-preserving refactor under spec 001
- [ ] Write the automated tests in `tests/001-push-to-talk-dictation/` and the manual checklist in `specs/001-.../manual-tests.md`; all green before proceeding
- [ ] Verify the **regeneration test**: could an agent rebuild `dictate.py` and
      `setup_autostart.sh` from the artifacts alone? Add missing detail where not.
- [ ] Add `.github/copilot-instructions.md` instructing agents to read the constitution
      and relevant spec before any code change, to update specs alongside code, and to
      write failing tests from acceptance criteria before implementing (red→green)
- [ ] (Optional) `specify init` to adopt GitHub Spec Kit slash commands

## 7. From then on: adding features

Follow the workflow in `AIDLC.md` §4–6. Candidate next features, with their entry points:

| Feature idea | Entry point | New spec folder |
|---|---|---|
| Custom hotkey (`--hotkey` flag) | PRD (user-visible) | `specs/002-custom-hotkey/` |
| Multi-language / language toggle | PRD | `specs/003-language-selection/` |
| Menu-bar status indicator | PRD + ADR (new UI component) | `specs/004-menubar-status/` |
| Tune silence threshold | Spec 001 (bug fix against REQ-006) | amend `specs/001-…` |
| Swap resampler for `scipy` | ADR (design change, same behavior) | amend plan of `specs/001-…` |

**Rule:** no change lands in `dictate.py` or `setup_autostart.sh` without a spec entry
that motivates it — drift between spec and code is a defect.
