import os
import ctypes
from ctypes import wintypes
import platform
import asyncio 
import requests
import aiohttp
import aiofiles
import subprocess
import winreg
import datetime
import json
import winshell
import psutil
import ctypes
from win32com.client import Dispatch
from PySide6.QtWidgets import QMessageBox

osu_files_url = "https://osu.ppy.sh/web/check-updates.php?action=check&stream=Stable40"
errpath = os.environ["LOCALAPPDATA"] + f"\\m1ppinstalllog-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"


def setuplog(level, text):
    match level:
        case 0:
            prefx = "INFO"
        case 1:
            prefx = "WARN"
        case 2:
            prefx = "ERROR"
        case 3:
            prefx = "CRITICAL"
    with open(errpath, 'a') as logfile:
        logfile.write(f"({datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}) [{prefx}] {text}\n")
        

def check_osu_install_path():
    setuplog(0, "Checking osu! install path...")
    if platform.system() == "Windows":
        try:
            aKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                  r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
                                  0, winreg.KEY_ALL_ACCESS)
            i = 0
            while True:
                try:
                    asubkey = winreg.EnumKey(aKey, i)
                    setuplog(0, f"Checking registry key: {asubkey}")
                except OSError:
                    setuplog(1, "No more registry keys.")
                    break

                try:
                    kKey = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall" + "\\" + asubkey
                    )
                    kValue = winreg.QueryValueEx(kKey, "DisplayName")
                except OSError:
                    i += 1
                    continue

                if kValue[0] == "osu!":
                    setuplog(0, "Found osu! installation entry.")
                    kValue2 = winreg.QueryValueEx(kKey, "DisplayIcon")
                    path = kValue2[0].replace("osu!.exe", "")
                    setuplog(0, f"osu! path resolved: {path}")
                    return path

                i += 1

        except WindowsError as e:
            setuplog(2, f"Registry access failed: {e}")
            return False

        setuplog(1, "osu! installation not found.")
        return False

    elif platform.system() == "Linux":
        setuplog(1, "osu! Linux path detection not implemented.")
        return False


def make_shortcut(target, path, wDir, icon):
    setuplog(0, f"Creating shortcut: {path}")
    try:
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()
        setuplog(0, f"Shortcut created successfully: {path}")
    except Exception as e:
        setuplog(2, f"Failed to create shortcut ({path}): {e}")


async def install_osu(m1pppath, osupath, curbar, curtext):
    setuplog(0, "Starting installation process...")

    try:
        if not os.path.isdir(m1pppath):
            setuplog(0, f"Creating installation directory: {m1pppath}")
            os.makedirs(m1pppath)

        setuplog(0, "Downloading file manifest...")
        update_data = requests.get(osu_files_url).json()
        filelen = len(update_data)
        setuplog(0, f"Files to install: {filelen}")

        total_files = 0

        async with aiohttp.ClientSession() as session:
            for file in update_data:
                url = file["url_full"]
                destination_file = os.path.join(m1pppath, file["filename"])
                setuplog(0, f"Downloading: {url}")
                curtext.setProperty("text", "Installing: " + destination_file + "\n\n")

                async with session.get(url) as response:
                    async with aiofiles.open(destination_file, 'wb') as f:
                        async for chunk in response.content.iter_chunked(1024):
                            if chunk:
                                try:
                                    await f.write(chunk)
                                except Exception as e:
                                    setuplog(3, f"Write error ({destination_file}): {e}")
                                    return False

                total_files += 1
                percent = total_files / filelen / 2
                curbar.setProperty("value", percent)
                setuplog(0, f"Downloaded {destination_file} ({percent*100:.1f}%)")


        async with aiohttp.ClientSession() as session:
            chunkstotal = 0
            url = "https://4ayo.ovh/m1pposu/files/launcher/latest/m1pplauncher.exe"
            destination_file = os.path.join(m1pppath, "m1pplauncher.exe")
            setuplog(0, f"Downloading launcher: {url}")
            curtext.setProperty("text", "Installing: " + destination_file + "\n\n")

            async with session.get(url) as response:
                totalsize = response.headers.get("Content-Length")
                setuplog(0, f"Launcher size: {totalsize} bytes")

                async with aiofiles.open(destination_file, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024):
                        if chunk:
                            try:
                                await f.write(chunk)
                                chunkstotal += 1024
                                percent = (chunkstotal / int(totalsize)) + 0.5
                                curbar.setProperty("value", percent)
                            except Exception as e:
                                setuplog(3, f"Write error (launcher): {e}")
                                return False

        installed_data = {"m1pppath": m1pppath, "osupath": osupath}
        json_path = os.path.join(m1pppath, 'installdata.json')
        with open(json_path, 'w') as f:
            json.dump(installed_data, f, indent=4)
        setuplog(0, f"Saved installation metadata to {json_path}")

        songs_link = os.path.join(m1pppath, "Songs")
        songs_target = os.path.join(osupath, "Songs")
        skins_link = os.path.join(m1pppath, "Skins")
        skins_target = os.path.join(osupath, "Skins")
        db_link = os.path.join(m1pppath, "osu!.db")
        db_target = os.path.join(osupath, "osu!.db")

        cmd_combined = (
            f'mklink /D "{songs_link}" "{songs_target}" && '
            f'mklink /D "{skins_link}" "{skins_target}" && '
            f'mklink "{db_link}" "{db_target}"'
        )

        setuplog(0, f"Executing mklink commands: {cmd_combined}")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f'/c "{cmd_combined}"', None, 0)

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\M1PPLauncher"
        setuplog(0, f"Creating registry uninstall entry: {key_path}")

        reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(reg_key, "DisplayName", 0, winreg.REG_SZ, "M1PP Launcher")
        winreg.SetValueEx(reg_key, "UninstallString", 0, winreg.REG_SZ, m1pppath + "\\m1pplauncher.exe uninstall")
        winreg.SetValueEx(reg_key, "Publisher", 0, winreg.REG_SZ, "M1PPosu")
        winreg.SetValueEx(reg_key, "InstallLocation", 0, winreg.REG_SZ, m1pppath)
        winreg.CloseKey(reg_key)
        setuplog(0, "Registry uninstall entry created.")

        desktop = winshell.desktop()
        startmenu = winshell.start_menu()
        setuplog(0, "Creating shortcuts...")

        try:
            make_shortcut(m1pppath + r"\m1pplauncher.exe",
                          desktop + r"\M1PP Launcher.lnk",
                          m1pppath,
                          m1pppath + r"\icon.ico")

            make_shortcut(m1pppath + r"\m1pplauncher.exe",
                          startmenu + r"\M1PP Launcher.lnk",
                          m1pppath,
                          m1pppath + r"\icon.ico")

        except Exception as e:
            setuplog(2, f"Shortcut creation failed: {e}")

        setuplog(0, "Installation completed successfully.")
        return True

    except Exception as e:
        setuplog(3, f"FATAL installer error: {e}")
        return False
