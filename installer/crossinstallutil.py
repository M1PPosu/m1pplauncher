import os
import sys
import shutil
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
from win32com.client import Dispatch
from PySide6.QtWidgets import QMessageBox
import m1pp_logger

osu_files_url = "https://osu.ppy.sh/web/check-updates.php?action=check&stream=Stable40"

errpath = m1pp_logger.get_log_path("installer")

def setuplog(level, text):
    logger = m1pp_logger.get_logger("installer")
    match level:
        case 0:
            logger.info(text)
        case 1:
            logger.warning(text)
        case 2:
            logger.error(text)
        case 3:
            logger.critical(text)
        case _:
            logger.info(text)

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def _copy_file(src_rel: str, dst_path: str):
    src = resource_path(src_rel)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.copy2(src, dst_path)

def _copy_dir(src_rel: str, dst_dir: str):
    src = resource_path(src_rel)
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copytree(src, dst_dir, dirs_exist_ok=True)

def check_osu_install_path():
    setuplog(0, "Checking osu! install path...")
    if platform.system() == "Windows":
        try:
            aKey = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
                0,
                winreg.KEY_ALL_ACCESS
            )
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
                    if not os.path.isfile(path + "\\osu!auth.dll"):
                        return 2
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
    setuplog(0, f"crossinstallutil path: {__file__}")
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
                percent = (total_files / filelen) * 0.5
                curbar.setProperty("value", percent)
                setuplog(0, f"Downloaded {destination_file} ({percent*100:.1f}%)")
                await asyncio.sleep(0)

        async with aiohttp.ClientSession() as session:
            chunkstotal = 0
            url = "https://4ayo.ovh/m1pposu/files/launcher/latest/v4B/m1pplauncher.exe"
            destination_file = os.path.join(m1pppath, "m1pplauncher.exe")
            setuplog(0, f"Downloading launcher: {url}")
            curtext.setProperty("text", "Installing: " + destination_file + "\n\n")

            async with session.get(url) as response:
                totalsize = response.headers.get("Content-Length")
                setuplog(0, f"Launcher size: {totalsize} bytes")

                totalsize_int = 0
                try:
                    if totalsize:
                        totalsize_int = int(totalsize)
                except Exception:
                    totalsize_int = 0

                async with aiofiles.open(destination_file, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024):
                        if chunk:
                            try:
                                await f.write(chunk)
                                chunkstotal += len(chunk)
                                if totalsize_int > 0:
                                    percent = 0.5 + (chunkstotal / totalsize_int) * 0.5
                                    if percent > 0.95:
                                        percent = 0.95
                                    curbar.setProperty("value", percent)
                                    await asyncio.sleep(0)
                            except Exception as e:
                                setuplog(3, f"Write error (launcher): {e}")
                                return False

        try:
            _copy_file("gui.qml", os.path.join(m1pppath, "gui.qml"))
            _copy_file("icon.png", os.path.join(m1pppath, "icon.png"))
            _copy_file("fade.png", os.path.join(m1pppath, "fade.png"))
            _copy_file("unknown.png", os.path.join(m1pppath, "unknown.png"))
            _copy_dir("slides", os.path.join(m1pppath, "slides"))
            _copy_dir("font", os.path.join(m1pppath, "font"))
            setuplog(0, "Copied UI assets (gui/slides/font) into install directory.")
        except Exception as e:
            setuplog(2, f"Failed copying UI assets: {e}")

        curtext.setProperty("text", "Finalizing: preparing...\n\n")
        curbar.setProperty("value", 0.96)
        await asyncio.sleep(0)

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

        collections_link = os.path.join(m1pppath, "collection.db")
        collections_target = os.path.join(osupath, "collection.db")

        username = os.environ.get("USERNAME", "").strip()
        user_cfg_name = f"osu!.{username}.cfg" if username else "osu!.cfg"

        settings_user_link = os.path.join(m1pppath, user_cfg_name)
        settings_user_target = os.path.join(osupath, user_cfg_name)

        settings_cfg_link = os.path.join(m1pppath, "osu!.cfg")
        settings_cfg_target = os.path.join(osupath, "osu!.cfg")

        cmd_combined = (
            f'mklink /D "{songs_link}" "{songs_target}" && '
            f'mklink /D "{skins_link}" "{skins_target}" && '
            f'mklink "{db_link}" "{db_target}" && '
            f'mklink "{collections_link}" "{collections_target}" && '
            f'mklink "{settings_user_link}" "{settings_user_target}" && '
            f'mklink "{settings_cfg_link}" "{settings_cfg_target}"'
        )

        curtext.setProperty("text", "Finalizing: creating links...\n\n")
        curbar.setProperty("value", 0.97)
        await asyncio.sleep(0)

        setuplog(0, f"Executing mklink commands: {cmd_combined}")
        try:
            completed = await asyncio.to_thread(
                subprocess.run,
                cmd_combined,
                shell=True,
                capture_output=True,
                text=True
            )
            if completed.returncode != 0:
                setuplog(2, f"mklink failed (code {completed.returncode})")
                setuplog(2, f"mklink stdout: {completed.stdout.strip()}")
                setuplog(2, f"mklink stderr: {completed.stderr.strip()}")
                return False
        except Exception as e:
            setuplog(3, f"mklink exception: {e}")
            return False

        curbar.setProperty("value", 0.98)
        await asyncio.sleep(0)

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\M1PPLauncher"
        setuplog(0, f"Creating registry uninstall entry: {key_path}")

        reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(reg_key, "DisplayName", 0, winreg.REG_SZ, "M1PP Launcher")
        winreg.SetValueEx(reg_key, "UninstallString", 0, winreg.REG_SZ, m1pppath + "\\m1pplauncher.exe uninstall")
        winreg.SetValueEx(reg_key, "Publisher", 0, winreg.REG_SZ, "M1PPosu")
        winreg.SetValueEx(reg_key, "InstallLocation", 0, winreg.REG_SZ, m1pppath)
        winreg.SetValueEx(reg_key, "DisplayIcon", 0, winreg.REG_SZ, m1pppath + "\\m1pplauncher.exe,0")
        winreg.CloseKey(reg_key)
        setuplog(0, "Registry uninstall entry created.")
        curbar.setProperty("value", 0.99)
        await asyncio.sleep(0)

        desktop = winshell.desktop()
        startmenu = winshell.start_menu()
        setuplog(0, "Creating shortcuts...")

        curtext.setProperty("text", "Finalizing: creating shortcuts...\n\n")
        curbar.setProperty("value", 0.995)
        await asyncio.sleep(0)

        try:
            make_shortcut(
                m1pppath + r"\m1pplauncher.exe",
                desktop + r"\M1PP Launcher.lnk",
                m1pppath,
                m1pppath + r"\m1pplauncher.exe,0"
            )

            make_shortcut(
                m1pppath + r"\m1pplauncher.exe",
                startmenu + r"\M1PP Launcher.lnk",
                m1pppath,
                m1pppath + r"\m1pplauncher.exe,0"
            )
        except Exception as e:
            setuplog(2, f"Shortcut creation failed: {e}")

        curtext.setProperty("text", "Installation completed.\n\n")
        curbar.setProperty("value", 1.0)
        await asyncio.sleep(0)

        setuplog(0, "Installation completed successfully.")
        return True

    except Exception as e:
        setuplog(3, f"FATAL installer error: {e}")
        return False
