import sys
import types
from pathlib import Path

# make dictate.py importable from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def _stub_module(name, module):
    try:
        __import__(name)
    except Exception:
        sys.modules[name] = module


# stub hardware/model deps so dictate.py imports without a mic, model, or permissions
_stub_module("mlx_whisper", types.ModuleType("mlx_whisper"))
_stub_module("sounddevice", types.ModuleType("sounddevice"))

_kb = types.ModuleType("pynput.keyboard")
_kb.Key = types.SimpleNamespace(alt_r="alt_r", cmd="cmd")
_kb.Controller = lambda: types.SimpleNamespace()
_kb.Listener = object
_pynput = types.ModuleType("pynput")
_pynput.keyboard = _kb
try:
    import pynput  # noqa: F401
except Exception:
    sys.modules["pynput"] = _pynput
    sys.modules["pynput.keyboard"] = _kb
