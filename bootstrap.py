import glob
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request
import zipfile
from ctypes import windll
from itertools import chain
from threading import Thread
from urllib.parse import urlparse

import psutil
import pyautogui

import util
import m1pp_logger

_log = m1pp_logger.get_logger("launcher")

RULESET_URLS = [
    "https://4ayo.ovh/m1pposu/files/authlib/authlibe.Rulesets.AuthlibInjection.dll",
    "https://github.com/MingxuanGame/LazerAuthlibInjection/releases/download/v2025.1026.0/osu.Game.Rulesets.AuthlibInjection.dll",
]

LAZER_RULESET_FILENAME = "osu.Game.Rulesets.AuthlibInjection.dll"


def messageerr(text):
    return windll.user32.MessageBoxW(0, text, "Error", 4112)


def _normalize_host(url_or_host: str) -> str:
    s = (url_or_host or "").strip()
    if not s:
        return s
    if "://" in s:
        u = urlparse(s)
        return (u.netloc or "").strip()
    return s.strip().rstrip("/")


def _download(url: str, dest_path: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "M1PPLauncher/4.0B"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(resp, f)


def load_mods(skipmods, osuplatform):
    configdata = util.get_configdata()
    modspath = os.path.join(configdata["m1pppath"], "mods")
    os.makedirs(modspath, exist_ok=True)

    moddata = {}
    existingmods = []
    conflicts = []

    for mod in chain.from_iterable(
        glob.iglob(path)
        for path in [
            f'{util.resource_path("builtinmods")}/*.mmod',
            f"{modspath}/*.mmod",
        ]
    ):
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
                if data.get("osuplatform") == "lazer" and osuplatform != "lazer":
                    shutil.rmtree(temp_dir_path, ignore_errors=True)
                    continue

                if data.get("osuplatform") == "stable" and osuplatform != "stable":
                    shutil.rmtree(temp_dir_path, ignore_errors=True)
                    continue

            existingmods.append(name)
            conflicts.extend(data.get("conflicts", []))
            moddata[temp_dir_path] = data

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

            payload_missing = set()
            payload_unexpected = set()
            if "payload" in data and isinstance(data["payload"], dict):
                payload_missing = expected_payload_keys - data["payload"].keys()
                payload_unexpected = data["payload"].keys() - expected_payload_keys
            else:
                payload_missing = expected_payload_keys

            if missing_keys or unexpected_keys or payload_missing or payload_unexpected:
                _log.warning("Invalid metadata JSON in mod: %s", mod)
                shutil.rmtree(temp_dir_path, ignore_errors=True)
                return ["Invalid metadata JSON", mod]

        except Exception as e:
            _log.exception("Failed to load mod %s", mod)
            shutil.rmtree(temp_dir_path, ignore_errors=True)
            return [e, mod]

    if len(existingmods) != len(set(existingmods)):
        _log.warning("Duplicate mods detected")
        return ["Duplicate mods detected", "your mods"]

    for modx in existingmods:
        if modx in conflicts:
            _log.warning("Incompatible mods detected (conflicts)")
            return ["Incompatible mods detected (mod conflicts)", "your mods"]

    return moddata


def _ensure_persistent_tool(exe_src: str, tool_name: str) -> tuple[str, str]:
    base = os.path.join(os.getenv("LOCALAPPDATA") or tempfile.gettempdir(), "M1PPLauncher", "tools", tool_name)
    os.makedirs(base, exist_ok=True)

    exe_dst = os.path.join(base, os.path.basename(exe_src))

    try:
        if (not os.path.isfile(exe_dst)) or (os.path.getsize(exe_dst) != os.path.getsize(exe_src)):
            shutil.copy2(exe_src, exe_dst)
    except Exception:
        if not os.path.isfile(exe_dst):
            shutil.copy2(exe_src, exe_dst)

    return exe_dst, base


def _is_process_running(name_lower: str) -> bool:
    try:
        for p in psutil.process_iter(["name"]):
            if (p.info.get("name") or "").lower() == name_lower:
                return True
    except Exception:
        pass
    return False


def _find_tosu_exe(mods) -> str:
    if not isinstance(mods, dict):
        return ""
    for mod_path, mod in mods.items():
        try:
            name = str(mod.get("name") or "").lower()
            payload = mod.get("payload") or {}
            exe = str(payload.get("executable") or "")
            exe_name = os.path.basename(exe).lower()
            if name == "tosu" or exe_name == "tosu.exe":
                return os.path.join(mod_path, exe)
        except Exception:
            continue
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

    def _log_pipe():
        try:
            if proc.stdout is None:
                return
            for line in iter(proc.stdout.readline, b""):
                if not line:
                    break
                _log.info("[tosu] %s", line.decode("utf-8", errors="replace").rstrip())
        except Exception:
            pass

    Thread(target=_log_pipe, daemon=True).start()


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


def _kill_by_name(name_lower: str):
    try:
        for p in psutil.process_iter(["name"]):
            if (p.info.get("name") or "").lower() == name_lower:
                try:
                    p.kill()
                except Exception:
                    pass
    except Exception:
        pass


def inject_mods(mods, ppid):
    time.sleep(3)

    for mod_path, mod in mods.items():
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        exe_path = os.path.join(mod_path, mod["payload"]["executable"])
        exe_name = os.path.basename(exe_path).lower()

        argss = mod["payload"]["arguments"]
        args = [arg.replace("%pid%", str(ppid)) for arg in argss]

        if exe_name == "tosu.exe":
            _kill_by_name("tosu.exe")
            exe_path, run_cwd = _ensure_persistent_tool(exe_path, "tosu")

            try:
                _spawn_logged_tosu(exe_path, run_cwd, startupinfo)
            except Exception:
                _log.exception("Injector failed (tosu). exe=%s", exe_path)

            continue

        startcmd = [exe_path]
        startcmd.extend(args)

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
                out = b""
                try:
                    out = modproc.communicate(timeout=mod["processtimeout"])[0] or b""
                except subprocess.TimeoutExpired:
                    try:
                        modproc.kill()
                    except Exception:
                        pass
                    out = b""

                code = modproc.returncode
                if code != 0:
                    _log.error("Mod injector exited non-zero. mod=%s code=%s", mod.get("name"), code)
                    if out:
                        _log.error(
                            "Mod output (%s): %s",
                            mod.get("name"),
                            out.decode("utf-8", errors="replace")[:2000],
                        )
                    Thread(
                        target=messageerr,
                        args=("Exit code: " + str(code) + "\n\n" + mod["errormessage"],),
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

    if os.path.isdir(configdata["m1pppath"]) and os.path.isdir(configdata["osupath"]):
        while True:
            try:
                for procx in psutil.process_iter():
                    if procx.name() == "osu!.exe":
                        procx.kill()
            except Exception:
                _log.exception("Failed killing existing osu!.exe processes")

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.Popen(
                [os.path.join(configdata["m1pppath"], "osu!.exe"), "-devserver", gameserver],
                cwd=configdata["m1pppath"],
                startupinfo=startupinfo,
            )

            lastproctime = time.time()
            injected = False
            lastpid = 0
            sentc = False
            osucc = False

            while True:
                process = None
                for p in psutil.process_iter(["pid", "name"]):
                    if p.info["name"] and p.info["name"].lower() == "osu!.exe":
                        lastproctime = time.time()
                        if lastpid == 0:
                            lastpid = p.pid
                        process = p
                        break

                if process is None:
                    gap = time.time() - lastproctime
                    grace = 2.05 if osucc else 120.0
                    if gap > grace:
                        return 0
                    time.sleep(0.1)
                    continue

                try:
                    windows = pyautogui.getAllWindows()
                except Exception:
                    _log.exception("pyautogui.getAllWindows() failed")
                    windows = []

                if not osucc:
                    for window in windows:
                        if window.title and window.title == "osu!" and window.width > 750:
                            try:
                                cmd = process.cmdline()
                            except Exception:
                                _log.exception("Failed reading osu!.exe cmdline()")
                                cmd = []

                            if gameserver not in cmd:
                                if not any(ext in cmd for ext in [".osk", ".osr", ".osu", ".osz", ".osb"]):
                                    try:
                                        for proc in psutil.process_iter():
                                            if proc.name() == "osu!.exe":
                                                proc.kill()
                                    except Exception:
                                        _log.exception("Failed killing osu!.exe during relaunch")
                                    return 9
                            else:
                                osucc = True

                        elif window.title and "cuttingedge" in window.title and not sentc:
                            Thread(
                                target=messageerr,
                                args=(
                                    'You are currently using the "cuttingedge" channel in osu!\nPlease switch to the Stable channel in order to keep playing on M1PP',
                                ),
                                daemon=True,
                            ).start()
                            sentc = True

                if not injected:
                    found = False
                    for window in windows:
                        if window.title and window.title == "osu!" and window.width > 750:
                            found = True
                            break

                    if found:
                        Thread(target=inject_mods, args=(mods, process.pid), daemon=True).start()
                        injected = True

                time.sleep(0.03)


def wait_to_hold():
    lastproctime = time.time()
    while True:
        found = False
        for p in psutil.process_iter(["pid", "name"]):
            if p.info["name"] and p.info["name"].lower() == "osu!.exe":
                lastproctime = time.time()
                found = True
                break

        if not found and (time.time() - lastproctime) > 1.3:
            return 0

        time.sleep(0.1)


def setup_settings_lazer():
    configdata = util.get_configdata()
    appdata_path = os.getenv("APPDATA") or ""
    if not appdata_path:
        _log.error("APPDATA missing; cannot install AuthlibInjection ruleset.")
        return False

    ruleset_cache = os.path.join(configdata["m1pppath"], "ruleset.dll")

    if not os.path.isfile(ruleset_cache):
        ok = False
        for url in RULESET_URLS:
            try:
                _log.info("Downloading AuthlibInjection ruleset: %s", url)
                _download(url, ruleset_cache)
                ok = True
                break
            except Exception as e:
                _log.warning("Ruleset download failed url=%s err=%s", url, e)
        if not ok:
            _log.error("Failed to download AuthlibInjection ruleset.")
            return False

    rulesets_dirs = [
        os.path.join(appdata_path, "osu", "rulesets"),
        os.path.join(appdata_path, "osu!", "rulesets"),
    ]

    installed = False
    for d in rulesets_dirs:
        try:
            os.makedirs(d, exist_ok=True)
            dst = os.path.join(d, LAZER_RULESET_FILENAME)
            shutil.copy2(ruleset_cache, dst)
            _log.info("Installed AuthlibInjection ruleset: %s", dst)
            installed = True
        except Exception as e:
            _log.warning("Failed installing ruleset into %s: %s", d, e)

    if not installed:
        _log.error("AuthlibInjection ruleset install failed; lazer will use Bancho.")
    return installed
def setup_osu_lazer():
    local_path = os.path.join(os.getenv("LOCALAPPDATA") or "", "osulazer", "current", "osu!.exe")

    api_host = _normalize_host("https://lazer-api.m1pposu.dev/")
    web_host = _normalize_host("https://lazer.m1pposu.dev/")

    if not setup_settings_lazer():
        _log.error("AuthlibInjection ruleset setup failed. Cannot route lazer to M1PP.")
        return False

    if not local_path or not os.path.isfile(local_path):
        _log.error("osu!lazer not found at expected path: %s", local_path)
        return False

    args = [
        local_path,
        f"--api-url={api_host}",
        f"--website-url={web_host}",
        "--disable-sentry-logger",
    ]

    try:
        _log.info("Launching osu!lazer: %s", " ".join(args))
        proc = subprocess.Popen(args)
        try:
            proc.wait(timeout=5)
            if proc.returncode not in (0, None):
                _log.warning("osu!lazer exited early code=%s", proc.returncode)
        except subprocess.TimeoutExpired:
            return True

        wait_to_hold()
        return True

    except Exception:
        _log.exception("setup_osu_lazer: launch failed")
        return False
