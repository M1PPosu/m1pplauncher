import asyncio
import subprocess
import json
import os
import psutil
import shutil
import zipfile
import tempfile
import glob
import pyautogui
import time
import util
from threading import Thread
from PySide6.QtWidgets import QMessageBox
from itertools import chain
import urllib.request
from ctypes import windll


def messageerr(text):
    return windll.user32.MessageBoxW(0, text, "Error", 4112)

def load_mods(skipmods, osuplatform):
    configdata = util.get_configdata()
    modspath = os.path.join(configdata["m1pppath"], "mods")
    os.makedirs(modspath, exist_ok=True)
    moddata = {}
    existingmods = []
    conflicts = []
    for mod in chain.from_iterable(glob.iglob(path) for path in [f'{util.resource_path("builtinmods")}/*.mmod', f'{modspath}/*.mmod']):
        temp_dir = tempfile.TemporaryDirectory(delete=False)
        try:
            with zipfile.ZipFile(mod, 'r') as zip_ref:
                zip_ref.extractall(temp_dir.name)
            data = json.loads(open(os.path.join(temp_dir.name, "manifest.json")).read())
            if data["name"] in skipmods:
                temp_dir.cleanup()
                continue
            if data["osuplatform"] == "lazer":
                if osuplatform != "lazer":
                    temp_dir.cleanup()
                    continue
            if data["osuplatform"] == "stable":
                if osuplatform != "stable":
                    temp_dir.cleanup()
                    continue
            existingmods.append(data["name"])
            conflicts.extend(data["conflicts"])
            moddata[temp_dir.name] = data
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
                "osuplatform"
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
            if (missing_keys or unexpected_keys or payload_missing or payload_unexpected):
                return ["Invalid metadata JSON", mod]
        except Exception as e:
            return [e, mod]
    if len(existingmods) != len(set(existingmods)):
        return ["Duplicate mods detected", "your mods"]
    for modx in existingmods:
        if modx in conflicts:
            return ["Incompatible mods detected (mod conflicts)", "your mods"]
    return moddata

def inject_mods(mods, ppid):
    time.sleep(3) # shitty way to fix injectors injecting too early
    for mod_path, mod in mods.items():
        print(mod_path)
        print(mod)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startcmd = [os.path.join(mod_path, mod["payload"]["executable"])]
        argss = mod["payload"]["arguments"]
        args = []
        for arg in argss:
            strnew = arg.replace("%pid%", str(ppid))
            args.append(strnew)
        startcmd.extend(args)
        print(startcmd)
        print("e")
        try:
            if mod["checkerror"] == True:
                modproc = subprocess.Popen(
                    startcmd,
                    startupinfo=startupinfo,
                    shell=True,
                    creationflags=subprocess.SW_HIDE,
                    stdout=subprocess.PIPE
                )
                print("e")
                modproc.communicate(timeout=mod["processtimeout"])[0]
                code = modproc.returncode
                if code != 0:
                    thread = Thread(target = messageerr, args = ("Exit code: " + str(code) + "\n\n" + mod["errormessage"],))
                    thread.start()
            else:
                subprocess.Popen(
                    startcmd,
                    shell=True,
                    creationflags=subprocess.SW_HIDE,
                    startupinfo=startupinfo
                )
                print("e")
        except:
            pass

# this is very hacky, osu! doesn't respect the -devserver argument when updating.
def launch_osu(gameserver, mods):
    configdata = util.get_configdata()

    if os.path.isdir(configdata["m1pppath"]) and os.path.isdir(configdata["osupath"]):
        dorun = True
        while dorun:

            try:
                for procx in psutil.process_iter():
                    if procx.name() == "osu!.exe":
                        procx.kill()
            except Exception as e:
                pass

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            proc = subprocess.Popen(
                [
                    os.path.join(configdata["m1pppath"], "osu!.exe"),
                    "-devserver",
                    gameserver
                ],
                cwd=configdata["m1pppath"],
                startupinfo=startupinfo
            )
            processc = True
            process = None
            lastproctime = time.time()
            injected = False
            stagec = False
            lastpid = 0
            sentc = False
            osucc = False
            while processc:
                for p in psutil.process_iter(['pid', 'name']):
                    if p.info['name'] and p.info['name'].lower() == 'osu!.exe':
                        lastproctime = time.time()
                        if lastpid == 0:
                            lastpid = p.pid
                        else:
                            stagec = True
                        process = p
                        break

                if time.time() - lastproctime > 2.05:
                    return 0
                
                try:
                    windows = pyautogui.getAllWindows()
                    if not osucc:
                        for window in windows:
                            if window.title and window.title == "osu!":
                                if window.width > 750:
                                    cmd = process.cmdline()
                                    if not gameserver in cmd:
                                        if not any(ext in cmd for ext in [".osk", ".osr", ".osu", ".osz", ".osb"]):
                                            for proc in psutil.process_iter():
                                                if proc.name() == "osu!.exe":
                                                    proc.kill()
                                                    return 9
                                    elif gameserver in cmd:
                                        osucc = True
                            elif window.title and "cuttingedge" in window.title and not sentc:
                                thread = Thread(target = messageerr, args = ('You are currently using the "cuttingedge" channel in osu!\nPlease switch to the Stable channel in order to keep playing on M1PP',), daemon=True)
                                thread.start()
                                sentc = True
                except:
                    return 0

                if not injected:
                    # osu! splashscreen has the title "osu! (loading)"
                    found = False
                    windows = pyautogui.getAllWindows()
                    for window in windows:
                        if window.title and window.title == "osu!":
                            if window.width > 750:
                                found = True
                    if found:
                        print(process.pid)
                        thread = Thread(target = inject_mods, args = (mods, process.pid,))
                        thread.start()
                        print("inj")
                        injected = True   
                time.sleep(0.03)
                    


def wait_to_hold(): 
    while True:
        for p in psutil.process_iter(['pid', 'name']):
            if p.info['name'] and p.info['name'].lower() == 'osu!.exe':
                lastproctime = time.time()
                break

        if time.time() - lastproctime > 1.3:
            return 0
        time.sleep(0.1)

def setup_settings_lazer():
    appdata_path = os.getenv("APPDATA")
    configdata = util.get_configdata()
    if appdata_path:
        pathdir = os.path.isfile(os.path.join(appdata_path, "osu", "rulesets", "osu.Game.Rulesets.AuthlibInjection.dll"))
    if not os.path.isfile(os.path.join(configdata["m1pppath"], "ruleset.dll")):
        url = "https://github.com/MingxuanGame/LazerAuthlibInjection/releases/download/v2025.1026.0/osu.Game.Rulesets.AuthlibInjection.dll"
        urllib.request.urlretrieve(url, os.path.join(configdata["m1pppath"], "ruleset.dll"))
    if not pathdir:
        shutil.copy(os.path.join(configdata["m1pppath"], "ruleset.dll"), os.path.join(appdata_path, "osu", "rulesets", "osu.Game.Rulesets.AuthlibInjection.dll"))
        return True
    return True

def unsetup_settings_lazer():
    appdata_path = os.getenv("APPDATA")
    if appdata_path:
        pathdir = os.path.isfile(os.path.join(appdata_path, "osu", "rulesets", "osu.Game.Rulesets.AuthlibInjection.dll"))
    if pathdir:
        os.remove(os.path.join(appdata_path, "osu", "rulesets", "osu.Game.Rulesets.AuthlibInjection.dll"))

def setup_osu_lazer():
    url = "https://github.com/ppy/osu/releases/latest/download/install.exe"
    local_path = os.path.join(os.getenv("LOCALAPPDATA"), "osulazer", "current", "osu!.exe")
    install_path = os.path.join(os.getenv("APPDATA"), "m1pplazer", "lazer-install.exe")
    todl = False
    try:
        setup_settings_lazer()
        proc = subprocess.Popen([local_path, "--api-url=lazer-api.m1pposu.dev", "--website-url=lazer.m1pposu.dev", "--disable-sentry-logger"])
        proc.wait(timeout=5)
        if proc.returncode != 0:
            todl = True
    except subprocess.TimeoutExpired:
        wait_to_hold()
        return True
    except Exception:
        todl = True
    try:
        if todl:
            urllib.request.urlretrieve(url, install_path)
            proc2 = subprocess.Popen([install_path])
            siter = True
            while siter:
                for w in pyautogui.getAllWindows():
                    if w.title == "osu!":
                        time.sleep(0.4) # im legit crashing out
                        for p in psutil.process_iter(['name']):
                            if p.info['name'] == "osu!.exe":
                                try:
                                    p.kill()
                                except:
                                    pass
                        while any(p.name() == "osu!.exe" for p in psutil.process_iter()):
                            time.sleep(0.1)

                        siter = False
                        break

    except Exception as ex:
        print(ex)
        return False
    try:
        setup_settings_lazer()
        proc = subprocess.Popen([local_path, "--api-url=lazer-api.m1pposu.dev", "--website-url=lazer.m1pposu.dev", "--disable-sentry-logger"])
        proc.wait()
        wait_to_hold()
        unsetup_settings_lazer() 
        return True     
    except Exception as ex:
        print(ex)
        return False