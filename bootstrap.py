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

def messageerr(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.setWindowTitle("Error")
    msg.exec_()

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
    time.sleep(3.45) # shitty way to fix injectors injecting too early
    for mod_path, mod in mods.items():
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
                    stdout=subprocess.PIPE
                )
                print("e")
                modproc.communicate(timeout=mod["processtimeout"])[0]
                code = modproc.returncode
                if code != 0:
                    thread = Thread(target = messageerr, args = ("Exit code: " + str(code) + "\n\n" + mod["errormessage"],))
                    thread.start()
            else: # avoid broken pipe errors
                subprocess.Popen(
                    startcmd,
                    startupinfo=startupinfo
                )
                print("e")
        except:
            pass

# this is very hacky, osu! doesn't respect the -devserver argument when updating.
def launch_osu(gameserver, mods):
    configdata = util.get_configdata()
    dorun = True
    if os.path.isdir(configdata["m1pppath"]) and os.path.isdir(configdata["osupath"]):
        while dorun:
            try:
                for procx in psutil.process_iter():
                    if procx.name() == "osu!.exe":
                        procx.kill()
            except:
                pass
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            proc = subprocess.Popen(
                [os.path.join(configdata["m1pppath"], "osu!.exe"),
                "-devserver", gameserver],
                cwd=configdata["m1pppath"],
                startupinfo=startupinfo
            )
            dorun = False
            checkserver = True
            safeclose = True
            injected = False
            try:
                while proc.poll() is None:
                    process = None
                    while process == None:
                        for p in psutil.process_iter(['pid','name']):
                            if p.info['name'] and p.info['name'].lower() == 'osu!.exe':
                                process = p
                                break
                        if not process == None:
                            break

                    if checkserver:
                        cmd = process.cmdline()
                        if not gameserver in cmd:
                            if not any(ext in cmd for ext in [".osk", ".osr", ".osu", ".osz", ".osb"]):
                                for proc in psutil.process_iter():
                                    if proc.name() == "osu!.exe":
                                        safeclose = False
                                        dorun = True
                                        proc.kill()
                        else:
                            if not injected:  
                                # osu! splashscreen has the title "osu! (loading)"
                                found = False
                                windows = pyautogui.getAllWindows()
                                for window in windows:
                                    if window.title == "osu!":
                                        found = True
                                if found:
                                    thread = Thread(target = inject_mods, args = (mods, proc.pid,))
                                    thread.start()
                                    injected = True

                   
                    
            except:
                try:
                    for procxx in psutil.process_iter():
                        if procxx.name() == "osu!.exe":
                            procxx.kill()  
                    continue
                except psutil.NoSuchProcess:
                    continue
            if not dorun:
                return 0
            else:
                continue
            if safeclose:
                return 0

        return 0
            
            
    else:
        return 1
    

def wait_to_hold(windowname, procname, checkinterval=0.5): 
    while True:
        windows = pyautogui.getAllWindows()
        if any(w.title == windowname for w in windows):
            break
        time.sleep(checkinterval)

    while True:
        proc_exists = any(
            p.info["name"] == procname
            for p in psutil.process_iter(["name"])
        )

        if not proc_exists:
            return True

        time.sleep(checkinterval)

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

def wait_to_kill(windowname, procname, delay = None):
    windows = pyautogui.getAllWindows()
    waitforlwin = True
    while waitforlwin:
        for window in windows:
            if window.title == windowname:
                try:
                    for procxx in psutil.process_iter():
                        if procxx.name() == procname:
                            if delay:
                                time.sleep(delay)
                            procxx.kill()
                            return True
                except psutil.NoSuchProcess:
                    return True

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
        wait_to_hold("osu!", "osu!.exe")
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
        wait_to_hold("osu!", "osu!.exe")
        unsetup_settings_lazer() 
        return True     
    except Exception as ex:
        print(ex)
        return False