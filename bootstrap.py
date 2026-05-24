import glob
import json
import os
import shutil
import subprocess
import tempfile
import time
import zipfile
from ctypes import windll
from itertools import chain
from threading import Thread

import psutil
import pyautogui

import util
import m1pp_logger

_log = m1pp_logger.get_logger("launcher")


def messageerr(text):
    return windll.user32.MessageBoxW(0, text, "Error", 4112)


def _mods_path() -> str:
    path = os.path.join(util.get_app_path(), "mods")
    os.makedirs(path, exist_ok=True)
    return path


def _osu_launch_dir(configdata: dict) -> str:
    for key in ("m1pppath", "osupath"):
        path = str(configdata.get(key) or "")
        if path and os.path.isfile(os.path.join(path, "osu!.exe")):
            return path
    return ""


def _ensure_persistent_tool(exe_src: str, tool_name: str) -> tuple[str, str]:
    base = os.path.join(os.getenv("LOCALAPPDATA") or tempfile.gettempdir(), "M1PPLauncher", "tools", tool_name)
    os.makedirs(base, exist_ok=True)

    exe_dst = os.path.join(base, os.path.basename(exe_src))

    if not os.path.isfile(exe_dst) or os.path.getsize(exe_dst) != os.path.getsize(exe_src):
        shutil.copy2(exe_src, exe_dst)

    return exe_dst, base


def _is_process_running(name_lower: str) -> bool:
    for proc in psutil.process_iter(["name"]):
        if (proc.info.get("name") or "").lower() == name_lower:
            return True
    return False


def _find_tosu_exe(mods) -> str:
    if not isinstance(mods, dict):
        return ""

    for mod_path, mod in mods.items():
        name = str(mod.get("name") or "").lower()
        payload = mod.get("payload") or {}
        exe = str(payload.get("executable") or "")
        exe_name = os.path.basename(exe).lower()

        if name == "tosu" or exe_name == "tosu.exe":
            return os.path.join(mod_path, exe)

    return ""


def _spawn_logged_tosu(exe_path: str, run_cwd: str, startupinfo) -> None:
    proc = subprocess.Popen(
        [exe_path],
        cwd=run_cwd,
        startupinfo=startupinfo,
        shell=False,
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    def log_pipe():
        if proc.stdout is None:
            return

        for line in iter(proc.stdout.readline, b""):
            if not line:
                break
            _log.info("[tosu] %s", line.decode("utf-8", errors="replace").rstrip())

    Thread(target=log_pipe, daemon=True).start()


def _kill_by_name(name_lower: str) -> None:
    for proc in psutil.process_iter(["name"]):
        if (proc.info.get("name") or "").lower() != name_lower:
            continue

        try:
            proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def load_mods(skipmods, osuplatform):
    modspath = _mods_path()
    moddata = {}
    existingmods = []
    conflicts = []

    mod_patterns = [
        f'{util.resource_path("builtinmods")}/*.mmod',
        f"{modspath}/*.mmod",
    ]

    for mod in chain.from_iterable(glob.iglob(path) for path in mod_patterns):
        temp_dir_path = tempfile.mkdtemp(prefix="m1ppmod_")

        try:
            with zipfile.ZipFile(mod, "r") as zip_ref:
                zip_ref.extractall(temp_dir_path)

            manifest_path = os.path.join(temp_dir_path, "manifest.json")
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            name = str(data.get("name") or "")
            name_lower = name.lower()

            if name in skipmods:
                shutil.rmtree(temp_dir_path, ignore_errors=True)
                continue

            if name_lower != "tosu":
                target_platform = data.get("osuplatform")
                if target_platform == "lazer" and osuplatform != "lazer":
                    shutil.rmtree(temp_dir_path, ignore_errors=True)
                    continue
                if target_platform == "stable" and osuplatform != "stable":
                    shutil.rmtree(temp_dir_path, ignore_errors=True)
                    continue

            expected_keys = {
                "name",
                "author",
                "version",
                "description",
                "platform",
                "conflicts",
                "payload",
                "checkerror",
                "errormessage",
                "processtimeout",
                "osuplatform",
            }
            expected_payload_keys = {"executable", "arguments"}

            missing_keys = expected_keys - data.keys()
            unexpected_keys = data.keys() - expected_keys

            payload = data.get("payload")
            if isinstance(payload, dict):
                payload_missing = expected_payload_keys - payload.keys()
                payload_unexpected = payload.keys() - expected_payload_keys
            else:
                payload_missing = expected_payload_keys
                payload_unexpected = set()

            if missing_keys or unexpected_keys or payload_missing or payload_unexpected:
                _log.warning("Invalid metadata JSON in mod: %s", mod)
                shutil.rmtree(temp_dir_path, ignore_errors=True)
                return ["Invalid metadata JSON", mod]

            existingmods.append(name)
            conflicts.extend(data.get("conflicts", []))
            moddata[temp_dir_path] = data

        except Exception as e:
            _log.exception("Failed to load mod %s", mod)
            shutil.rmtree(temp_dir_path, ignore_errors=True)
            return [e, mod]

    if len(existingmods) != len(set(existingmods)):
        _log.warning("Duplicate mods detected")
        return ["Duplicate mods detected", "your mods"]

    for mod_name in existingmods:
        if mod_name in conflicts:
            _log.warning("Incompatible mods detected")
            return ["Incompatible mods detected (mod conflicts)", "your mods"]

    return moddata


def ensure_tosu_running(mods=None) -> bool:
    if _is_process_running("tosu.exe"):
        return True

    exe_src = _find_tosu_exe(mods)
    if not exe_src or not os.path.isfile(exe_src):
        return False

    exe_path, run_cwd = _ensure_persistent_tool(exe_src, "tosu")

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        _spawn_logged_tosu(exe_path, run_cwd, startupinfo)
        return True
    except Exception:
        _log.exception("Failed to start tosu")
        return False


def inject_mods(mods, ppid):
    time.sleep(3)

    for mod_path, mod in mods.items():
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        exe_path = os.path.join(mod_path, mod["payload"]["executable"])
        exe_name = os.path.basename(exe_path).lower()
        args = [arg.replace("%pid%", str(ppid)) for arg in mod["payload"]["arguments"]]

        if exe_name == "tosu.exe":
            _kill_by_name("tosu.exe")
            exe_path, run_cwd = _ensure_persistent_tool(exe_path, "tosu")

            try:
                _spawn_logged_tosu(exe_path, run_cwd, startupinfo)
            except Exception:
                _log.exception("Injector failed for tosu. exe=%s", exe_path)

            continue

        startcmd = [exe_path, *args]

        try:
            if mod.get("checkerror") is True:
                modproc = subprocess.Popen(
                    startcmd,
                    cwd=mod_path,
                    startupinfo=startupinfo,
                    shell=True,
                    creationflags=subprocess.SW_HIDE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )

                try:
                    out = modproc.communicate(timeout=mod["processtimeout"])[0] or b""
                except subprocess.TimeoutExpired:
                    modproc.kill()
                    out = b""

                if modproc.returncode != 0:
                    _log.error("Mod injector exited non-zero. mod=%s code=%s", mod.get("name"), modproc.returncode)
                    if out:
                        _log.error("Mod output (%s): %s", mod.get("name"), out.decode("utf-8", errors="replace")[:2000])

                    Thread(
                        target=messageerr,
                        args=("Exit code: " + str(modproc.returncode) + "\n\n" + mod["errormessage"],),
                        daemon=True,
                    ).start()
            else:
                subprocess.Popen(
                    startcmd,
                    cwd=mod_path,
                    shell=True,
                    creationflags=subprocess.SW_HIDE,
                    startupinfo=startupinfo,
                )

        except Exception:
            _log.exception("Injector failed. mod=%s cmd=%s", mod.get("name"), startcmd)


def launch_osu(gameserver, mods):
    configdata = util.get_configdata()
    launch_dir = _osu_launch_dir(configdata)

    if not launch_dir:
        _log.error("Cannot launch osu!: installdata.json does not point to a valid osu!.exe")
        return 1

    _kill_by_name("osu!.exe")

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    subprocess.Popen(
        [os.path.join(launch_dir, "osu!.exe"), "-devserver", gameserver],
        cwd=launch_dir,
        startupinfo=startupinfo,
    )

    deadline = time.time() + 120.0
    warned_cuttingedge = False

    while time.time() < deadline:
        process = None

        for proc in psutil.process_iter(["pid", "name"]):
            if (proc.info.get("name") or "").lower() == "osu!.exe":
                process = proc
                break

        if process is None:
            time.sleep(0.1)
            continue

        try:
            windows = pyautogui.getAllWindows()
        except Exception:
            _log.exception("pyautogui.getAllWindows() failed")
            windows = []

        for window in windows:
            if window.title and "cuttingedge" in window.title and not warned_cuttingedge:
                Thread(
                    target=messageerr,
                    args=(
                        'You are currently using the "cuttingedge" channel in osu!\n'
                        "Please switch to the Stable channel in order to keep playing on M1PP",
                    ),
                    daemon=True,
                ).start()
                warned_cuttingedge = True

        found_osu_window = any(window.title == "osu!" and window.width > 750 for window in windows)
        if not found_osu_window:
            time.sleep(0.05)
            continue

        try:
            cmd = process.cmdline()
        except psutil.Error:
            _log.exception("Failed reading osu!.exe cmdline")
            cmd = []

        if gameserver not in cmd:
            opened_file = any(ext in cmd for ext in [".osk", ".osr", ".osu", ".osz", ".osb"])
            if not opened_file:
                _kill_by_name("osu!.exe")
                return 9

        Thread(target=inject_mods, args=(mods, process.pid), daemon=True).start()
        return 0

    _log.warning("Timed out waiting for osu! window after launch")
    return 0