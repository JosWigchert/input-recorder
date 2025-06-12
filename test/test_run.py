import json
import importlib.util
import sys
from pathlib import Path
import types

class DummyButton:
    def config(self, **kwargs):
        pass

class DummyKeyboardController:
    def press(self, key):
        pass
    def release(self, key):
        pass

class DummyMouseController:
    def __init__(self):
        self.position = (0, 0)
    def press(self, button):
        pass
    def release(self, button):
        pass

# Stub external modules so main can be imported without dependencies installed
kb_stub = types.ModuleType("keyboard")
kb_stub.add_hotkey = lambda *a, **k: None
sys.modules.setdefault("keyboard", kb_stub)

pn_keyboard = types.ModuleType("pynput.keyboard")
pn_keyboard.Controller = DummyKeyboardController
pn_keyboard.KeyCode = types.SimpleNamespace(from_vk=lambda vk: vk)

pn_mouse = types.ModuleType("pynput.mouse")
pn_mouse.Controller = DummyMouseController
pn_mouse.Button = types.SimpleNamespace()

pn_stub = types.ModuleType("pynput")
pn_stub.keyboard = pn_keyboard
pn_stub.mouse = pn_mouse
sys.modules.setdefault("pynput", pn_stub)
sys.modules.setdefault("pynput.keyboard", pn_keyboard)
sys.modules.setdefault("pynput.mouse", pn_mouse)

spec = importlib.util.spec_from_file_location(
    "main", Path(__file__).resolve().parents[1] / "main.py"
)
main = importlib.util.module_from_spec(spec)
sys.modules["main"] = main
spec.loader.exec_module(main)

RecorderApp = main.RecorderApp

def test_run_recorded_actions_countdown(monkeypatch, capsys, tmp_path):
    dummy = RecorderApp.__new__(RecorderApp)
    dummy.record_button = DummyButton()
    dummy.run_button = DummyButton()

    actions = [
        {"device": "keyboard", "time": 0, "data": {"key": 65, "name": "a", "action": "down"}}
    ]
    file_path = tmp_path / "actions.json"
    file_path.write_text(json.dumps(actions))

    monkeypatch.setattr("time.sleep", lambda x: None)

    dummy.run_recorded_actions(str(file_path))
    out = capsys.readouterr().out
    assert out.count("3 ") == 1
    assert "Running commands in " in out
