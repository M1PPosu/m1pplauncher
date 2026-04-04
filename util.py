import os
import sys
import json

_DEFAULT_SETTINGS = {"id0": 1, "id1": 1, "id11": 1, "id111": 0}

def get_app_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _read_json_file(path: str, default):
    try:
        if not os.path.isfile(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _write_json_file(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)

def get_configdata() -> dict:
    path = os.path.join(get_app_path(), "installdata.json")
    data = _read_json_file(path, default={})
    if not isinstance(data, dict):
        data = {}
    data.setdefault("m1pppath", "")
    data.setdefault("osupath", "")
    return data

def resource_path(relative_path: str) -> str:
    external = os.path.join(get_app_path(), relative_path)
    if os.path.exists(external):
        return external

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def _coerce_setting_value(key: str, value) -> int:
    default_value = _DEFAULT_SETTINGS.get(key, 0)
    try:
        v = int(value)
    except Exception:
        return default_value
    if v not in (0, 1):
        return default_value
    return v

def config_setup():
    targetfile = os.path.join(get_app_path(), "launchersettings.json")

    data = _read_json_file(targetfile, default=None)
    if not isinstance(data, dict):
        data = dict(_DEFAULT_SETTINGS)
        _write_json_file(targetfile, data)

    normalized = {}
    for key in _DEFAULT_SETTINGS.keys():
        normalized[key] = _coerce_setting_value(key, data.get(key, _DEFAULT_SETTINGS[key]))

    if data != normalized:
        data = normalized
        _write_json_file(targetfile, data)
    else:
        data = normalized

    return dict(data), data["id0"], data["id1"], data["id11"], data["id111"]

def config_set_value(key, value):
    targetfile = os.path.join(get_app_path(), "launchersettings.json")
    data = _read_json_file(targetfile, default=dict(_DEFAULT_SETTINGS))
    if not isinstance(data, dict):
        data = dict(_DEFAULT_SETTINGS)

    if key not in _DEFAULT_SETTINGS:
        return

    data[key] = _coerce_setting_value(key, value)
    _write_json_file(targetfile, data)

def config_read_value(key):
    targetfile = os.path.join(get_app_path(), "launchersettings.json")
    data = _read_json_file(targetfile, default=dict(_DEFAULT_SETTINGS))
    if not isinstance(data, dict):
        data = dict(_DEFAULT_SETTINGS)

    if key not in _DEFAULT_SETTINGS:
        return 0

    return _coerce_setting_value(key, data.get(key, _DEFAULT_SETTINGS[key]))
