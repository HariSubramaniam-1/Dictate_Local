#!/usr/bin/env python3
"""
Local push-to-talk dictation for macOS (Apple Silicon). Fully offline.

Usage: hold RIGHT OPTION, speak, release -> text is pasted into the focused app.

Setup:
  1. Python env:
       python3 -m venv ~/dictate-env && source ~/dictate-env/bin/activate
       pip install mlx-whisper sounddevice numpy pynput
  2. Model (one-time, via browser):
       huggingface.co/mlx-community/whisper-large-v3-turbo -> Files and versions
       Download config.json + weights.safetensors into ./models/ (next to this script)
  3. Run:
       python3 dictate.py
       python3 dictate.py --list-devices          # show microphones
       python3 dictate.py --device "MacBook Pro"  # always use a specific mic (name or index)

macOS permissions (System Settings > Privacy & Security) for Terminal, which runs dictate.py:
  Microphone, Accessibility (to paste), Input Monitoring (to see the hotkey)

Autostart at login: bash setup_autostart.sh   (see README.md)
"""
import argparse
import os
import subprocess
import sys
import threading
import time

import mlx_whisper
import numpy as np
import sounddevice as sd
from pynput import keyboard

MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
HOTKEY = keyboard.Key.alt_r                      # right Option key
LANGUAGE = "en"
WHISPER_RATE = 16000                             # Whisper expects 16 kHz
MIN_SECONDS = 0.3                                # ignore accidental taps
SILENCE_RMS = 0.002                              # below this = no speech captured
HALLUCINATIONS = {"thank you.", "thank you", "thanks for watching!", "you", "."}

frames = []
recording = False
mic_rate = WHISPER_RATE
device_choice = None                             # None = current system default mic
stream = None
frames_lock = threading.Lock()
stream_lock = threading.Lock()
kb = keyboard.Controller()


def beep(sound):
    subprocess.Popen(["afplay", f"/System/Library/Sounds/{sound}.aiff"])


def audio_callback(indata, n_frames, t, status):
    if recording:
        with frames_lock:
            frames.append(indata[:, 0].copy())


def start_stream():
    """Open the mic fresh on every press so device switches (AirPods <-> built-in) are picked up."""
    global stream, mic_rate
    with stream_lock:
        try:
            sd._terminate()                      # refresh PortAudio's device list
            sd._initialize()
            dev = sd.query_devices(device_choice, kind="input")
            mic_rate = int(dev["default_samplerate"])
            s = sd.InputStream(device=dev["index"], samplerate=mic_rate, channels=1,
                               dtype="float32", callback=audio_callback)
            s.start()
            print(f"Mic: {dev['name']} @ {mic_rate} Hz")
            if recording:
                stream = s
            else:                                # key already released
                s.stop()
                s.close()
        except Exception as e:
            print(f"Mic error: {e}")
            stream = None


def stop_stream():
    global stream
    with stream_lock:
        if stream is not None:
            stream.stop()
            stream.close()
            stream = None


def resample(audio, src_rate, dst_rate=WHISPER_RATE):
    """Convert mic's native rate to 16 kHz for Whisper."""
    if src_rate == dst_rate:
        return audio
    n_out = int(len(audio) * dst_rate / src_rate)
    x_old = np.linspace(0, 1, len(audio), endpoint=False)
    x_new = np.linspace(0, 1, n_out, endpoint=False)
    return np.interp(x_new, x_old, audio).astype(np.float32)


def should_transcribe(audio):
    """Gate 16 kHz audio: returns (ok, reason, rms). Short clips fail silently."""
    if len(audio) < WHISPER_RATE * MIN_SECONDS:
        return False, None, 0.0
    rms = float(np.sqrt(np.mean(audio ** 2)))
    if rms < SILENCE_RMS:
        return False, (f"Silent audio (level {rms:.5f}) - mic muted, wrong device, "
                       "or Microphone permission missing."), rms
    return True, None, rms


def is_hallucination(text):
    return text.lower() in HALLUCINATIONS


def paste(text):
    """Paste via clipboard, then restore the previous clipboard text."""
    previous = subprocess.run(["pbpaste"], capture_output=True).stdout
    subprocess.run(["pbcopy"], input=text.encode("utf-8"))
    with kb.pressed(keyboard.Key.cmd):
        kb.press("v")
        kb.release("v")
    time.sleep(0.3)
    subprocess.run(["pbcopy"], input=previous)


def finish():
    global frames
    stop_stream()
    with frames_lock:
        chunk, frames = frames, []
    if not chunk:
        print("No audio captured - check Microphone permission / device.")
        return
    audio = resample(np.concatenate(chunk).astype(np.float32), mic_rate)
    ok, reason, rms = should_transcribe(audio)
    if not ok:
        if reason:
            print(reason)
        return
    t0 = time.time()
    result = mlx_whisper.transcribe(audio, path_or_hf_repo=MODEL, language=LANGUAGE,
                                    condition_on_previous_text=False)
    text = result["text"].strip()
    print(f"[{time.time() - t0:.1f}s, level {rms:.4f}] {text}")
    if text and not is_hallucination(text):
        paste(text + " ")


def on_press(key):
    global recording, frames
    if key == HOTKEY and not recording:
        with frames_lock:
            frames = []
        recording = True
        beep("Tink")
        threading.Thread(target=start_stream, daemon=True).start()


def on_release(key):
    global recording
    if key == HOTKEY and recording:
        recording = False
        beep("Pop")
        threading.Thread(target=finish, daemon=True).start()


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--device", default=None, help="mic index or part of its name")
    return parser


def parse_device(value):
    """Digits pin a device index; anything else matches by name substring."""
    return int(value) if value.isdigit() else value


def ensure_model(model_dir=MODEL):
    if not os.path.isfile(os.path.join(model_dir, "config.json")):
        sys.exit(f"Model not found in {model_dir} (need config.json + weights.safetensors)")


def main():
    global device_choice
    args = build_parser().parse_args()

    if args.list_devices:
        print(sd.query_devices())
        return

    if args.device is not None:
        device_choice = parse_device(args.device)

    ensure_model()

    print("Loading model (warm-up)...")
    mlx_whisper.transcribe(np.zeros(WHISPER_RATE, dtype=np.float32), path_or_hf_repo=MODEL)
    print("Ready. Hold RIGHT OPTION to dictate. Ctrl+C to quit.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
