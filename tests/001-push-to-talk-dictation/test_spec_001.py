"""Automated acceptance tests for specs/001-push-to-talk-dictation/spec.md.

Each test names the REQ it verifies. Manual REQs live in manual-tests.md.
"""
import numpy as np
import pytest

import dictate


def sine(freq_hz, seconds, rate, amplitude=0.5):
    t = np.linspace(0, seconds, int(rate * seconds), endpoint=False)
    return (amplitude * np.sin(2 * np.pi * freq_hz * t)).astype(np.float32)


# REQ-004: audio is resampled from the mic's native rate to 16 kHz
@pytest.mark.parametrize("src_rate", [48000, 24000])
def test_req_004_resample_length_and_frequency(src_rate):
    out = dictate.resample(sine(440, 1.0, src_rate), src_rate)
    assert len(out) == dictate.WHISPER_RATE
    assert out.dtype == np.float32
    spectrum = np.abs(np.fft.rfft(out))
    peak_hz = np.argmax(spectrum) * dictate.WHISPER_RATE / len(out)
    assert abs(peak_hz - 440) < 5


def test_req_004_same_rate_passthrough():
    audio = sine(440, 1.0, dictate.WHISPER_RATE)
    assert dictate.resample(audio, dictate.WHISPER_RATE) is audio


# REQ-005: clips shorter than 0.3 s are discarded silently (no diagnostic)
def test_req_005_short_clip_discarded():
    ok, reason, _ = dictate.should_transcribe(sine(440, 0.1, dictate.WHISPER_RATE))
    assert not ok
    assert reason is None


# REQ-006: clips with RMS below 0.002 are discarded with a diagnostic message
def test_req_006_silent_clip_discarded_with_message():
    silent = np.zeros(dictate.WHISPER_RATE, dtype=np.float32)
    ok, reason, _ = dictate.should_transcribe(silent)
    assert not ok
    assert "Silent audio" in reason


def test_req_006_normal_speech_passes_gate():
    ok, reason, rms = dictate.should_transcribe(sine(440, 1.0, dictate.WHISPER_RATE))
    assert ok
    assert reason is None
    assert rms > dictate.SILENCE_RMS


# REQ-007: known hallucination strings are suppressed, normal text passes
@pytest.mark.parametrize("text", ["Thank you.", "Thank you", "Thanks for watching!", "You", "."])
def test_req_007_hallucinations_suppressed(text):
    assert dictate.is_hallucination(text)


def test_req_007_normal_text_passes():
    assert not dictate.is_hallucination("Send the report by Friday.")


# REQ-010: --list-devices flag is parsed
def test_req_010_list_devices_flag():
    args = dictate.build_parser().parse_args(["--list-devices"])
    assert args.list_devices is True
    assert dictate.build_parser().parse_args([]).list_devices is False


# REQ-011: --device accepts an index (digits) or a name substring
def test_req_011_device_parsing():
    assert dictate.build_parser().parse_args(["--device", "2"]).device == "2"
    assert dictate.parse_device("2") == 2
    assert dictate.parse_device("MacBook Pro") == "MacBook Pro"


# REQ-012: startup fails with a clear error if model files are missing
def test_req_012_missing_model_exits(tmp_path):
    with pytest.raises(SystemExit) as exc:
        dictate.ensure_model(str(tmp_path))
    assert "Model not found" in str(exc.value)


def test_req_012_present_model_passes(tmp_path):
    (tmp_path / "config.json").write_text("{}")
    dictate.ensure_model(str(tmp_path))  # must not raise


# REQ-014: transcription language is English
def test_req_014_language_is_english():
    assert dictate.LANGUAGE == "en"
