import sys
import os
import psutil
import shutil
import bootstrap
import PySide6.QtAsyncio as QtAsyncio
import asyncio
import tempfile
import requests
import qasync
import util
import json
import ctypes
import winreg
from ctypes import wintypes
import winshell
import subprocess
import webbrowser
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QObject, Slot, QUrl, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtQml import QQmlApplicationEngine

def is_admin():
    try:
        admin = ctypes.windll.shell32.IsUserAnAdmin()
        return admin
    except Exception as e:
        return False

LOCALAPPDATA = os.environ.get("LOCALAPPDATA")

UNINSTALL_SIGNAL = LOCALAPPDATA + "\\uninstall_pending.txt"

def uninstall():
    if not is_admin():
        try:
            with open(UNINSTALL_SIGNAL, "w", encoding="utf-8") as f:
                f.write("uninstall")
        except Exception as e:
            print("Failed to write uninstall signal:", e)

        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            None,
            None,
            1
        )
        sys.exit(0)

    try:
        with open(os.path.join(util.get_app_path(), "installdata.json"), "r", encoding="utf-8") as f:
            data = json.load(f)

        mipath = data["m1pppath"]

        for proc in psutil.process_iter(attrs=["name"]):
            try:
                if proc.info["name"] == "tosu.exe":
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.DeleteFileW.argtypes = k32.RemoveDirectoryW.argtypes = [wintypes.LPCWSTR]
        k32.DeleteFileW(os.path.join(mipath, "osu!.db"))
        k32.RemoveDirectoryW(os.path.join(mipath, "Songs"))
        k32.RemoveDirectoryW(os.path.join(mipath, "Skins"))

        uninstall_key = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\M1PPLauncher"
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, uninstall_key)
        except FileNotFoundError:
            pass
        except OSError as e:
            print("Registry cleanup error:", e)

        try:
            desktop = winshell.desktop()
            startmenu = winshell.start_menu()
            for path in (
                os.path.join(desktop, "M1PP Launcher.lnk"),
                os.path.join(startmenu, "M1PP Launcher.lnk"),
            ):
                if os.path.exists(path):
                    os.remove(path)
        except Exception as e:
            sys.exit(0)

        pid = os.getpid()

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        os.remove(UNINSTALL_SIGNAL)

        updater_src = util.resource_path("m1ppupdater.exe")
        temp_dir = tempfile.mkdtemp(prefix="m1pp_uninstaller_")
        updater_dst = os.path.join(temp_dir, "m1ppupdater.exe")
        shutil.copy2(updater_src, updater_dst)

        ctypes.windll.shell32.ShellExecuteW(None, "runas", updater_dst, f'finishuninstall {pid} "{mipath}"', None, 1)

    except Exception as e:
        print("FATAL uninstall error:", e)

    finally:
        try:
            os.remove(UNINSTALL_SIGNAL)
        except FileNotFoundError:
            pass

    sys.exit(0)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_obj = None
        self.isonline = "Online"
        self.newsupdated = False
        self.newslink = "https://m1pposu.dev"
        try:
            req = requests.get("http://google.com")
            req.raise_for_status()
        except:
            self.isonline = "Offline"
    def run(self):
        sys.exit(QApplication.instance().exec())

    def set_qml_root(self, root):
        self.root_obj = root
        try:
            self.updatenews()
        except Exception as e:
            print(e)
            self.isonline += " (Disconnected)"
        file, self.relaxpatcher, self.tosu, self.debuginfo, self.customstate = util.config_setup()
        for name, value in file.items():
            if not name == "id10":
                self.root_obj.findChild(QObject, name).setProperty("checked", value)
        sel = self.root_obj.findChild(QObject, "serversel")
        inp = self.root_obj.findChild(QObject, "serverinp")
        if self.customstate == 0:
            inp.setProperty("visible", False)
            sel.setProperty("visible", True)
        else:
            inp.setProperty("visible", True)
            sel.setProperty("visible", False)
        dbg = self.root_obj.findChild(QObject, "dbg")
        dbg1 = self.root_obj.findChild(QObject, "dbg1")
        dbg2 = self.root_obj.findChild(QObject, "dbg2")
        if self.debuginfo == 0:
            dbg.setProperty("visible", False)
            dbg1.setProperty("visible", False)
            dbg2.setProperty("visible", False)
        else:
            dbg.setProperty("visible", True)
            dbg1.setProperty("visible", True)
            dbg2.setProperty("visible", True)
        self.update_info_stats()
        

    def updatenews(self):
        recv = requests.get("https://4ayo.ovh/m1pposu/news/news.json", timeout=2).json()
        arrx = util.get_configdata()
        if recv["current_version"].strip().upper() != "BETA3":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setText(f'New version of M1PPLauncher has been released! Would you like to download it? ({recv["current_version"]})')
            msg.setWindowTitle("Update available!")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)

            response = msg.exec()

            if response == QMessageBox.Yes:
                updater_src = util.resource_path("m1ppupdater.exe")
                temp_dir = tempfile.mkdtemp(prefix="m1pp_updater_")
                updater_dst = os.path.join(temp_dir, "m1ppupdater.exe")
                shutil.copy2(updater_src, updater_dst)

                ctypes.windll.shell32.ShellExecuteW(None, "runas", updater_dst, f'"{arrx["m1pppath"]}"', None, 1)

                sys.exit(0)
        newsbtn = self.root_obj.findChild(QObject, "newsbtn")
        newstext = self.root_obj.findChild(QObject, "newstext")
        newsimg = self.root_obj.findChild(QObject, "newsimg")

        newsbtn.setProperty("text", recv["btntext"])
        newsbtn.setProperty("visible", recv["btnvisible"])
        self.newslink = recv["btnlink"]

        newstext.setProperty("text", recv["title"])

        newsimg.setProperty("source", recv["imglink"])



    def update_info_stats(self):
        configdata = util.get_configdata()
        modsenabled = 0
        customstatus = "Disabled"

        if util.config_read_value("id0") == 1:
            modsenabled += 1
        if util.config_read_value("id1") == 1:
            modsenabled += 1
        for ffile in os.listdir(os.path.join(configdata["m1pppath"], "mods")):
            if ffile.lower().endswith(".mmod"):
                modsenabled += 1
        svst = self.root_obj.findChild(QObject, "serversel")
        server = svst.property("currentIndex")
        if server == 0:
            osuplatform = "Stable"
        elif server == 1:
            osuplatform = "Lazer"
        if util.config_read_value("id111") != 0:
            svst = self.root_obj.findChild(QObject, "serverinp")
            osuplatform = "Stable"
            customstatus = "Enabled"
        statusbox = self.root_obj.findChild(QObject, "dbg")
        strnow = f"\n\nClient channel: {osuplatform}\nLoaded mods: {modsenabled}\nConnection: {self.isonline}\nCustom server: {customstatus}"
        statusbox.setProperty("text", strnow)

    @qasync.asyncSlot(int, int)
    async def execguifn(self, index, status):
        print(f'index: {index}')
        print(f'status: {status}')
        if index == 880811:
            self.update_info_stats()
        if index == 2137:
            try:
                platform = "stable"
                if util.config_read_value("id111") == 0:
                    svst = self.root_obj.findChild(QObject, "serversel")
                    server = svst.property("currentIndex")
                    if server == 0:
                        gameserver = 10
                    elif server == 1:
                        gameserver = 20
                        platform = "lazer"
                print("INFO: Bootstraping...")
                playbtn = self.root_obj.findChild(QObject, "playbtn")
                playbtn.setProperty("enabled", False)
                playbtn.setProperty("text", "LOADING MODS")
                dismods = []
                id0 = util.config_read_value("id0")
                id1 = util.config_read_value("id1")
                if id0 == 0:
                    dismods.append("RelaxPatcher")
                if id1 == 0:
                    dismods.append("tosu")
                
                mods = await asyncio.to_thread(bootstrap.load_mods, dismods, platform)
                if isinstance(mods, list):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText(f"An error has occured during loading {mods[1]}\n\nError message: {mods[0]}")
                    msg.setWindowTitle("Mod loader error")
                    msg.exec_()
                else:
                    print(mods)
                    #if util.config_read_value("id10") == 1:
                    #    self.hide()

                    if util.config_read_value("id111") != 0:
                        svst = self.root_obj.findChild(QObject, "serverinp")
                        server = svst.property("displayText")
                        if server != "ppy.sh" and server != "":
                            gameserver = server
                        else:
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Critical)
                            msg.setText("We have detected that you are trying to connect to the official Bancho servers.\nWe disallow this to keep your account safe. Mods used here inject directly into the osu! process or even modify the game files.\nSuch actions are likely to trigger an autoban on Bancho.")
                            msg.setWindowTitle("Error")
                            msg.exec_()
                            playbtn.setProperty("enabled", True)
                            playbtn.setProperty("text", "LAUNCH")    
                            return   
                    if gameserver != 20:
                        if gameserver == 10:
                            gameserver = "m1pposu.dev"
                        playbtn.setProperty("text", "LAUNCHING")
                        print(mods)
                        bootstrap_result = await asyncio.to_thread(bootstrap.launch_osu, gameserver, mods)
                        
                        if bootstrap_result == 1:
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Critical)
                            msg.setText("Your M1PP Launcher installation is corrupted! Please try reinstalling the launcher.")
                            msg.setWindowTitle("Error")
                            msg.exec_()
                        if bootstrap_result == 9:
                            isgd = True
                            while isgd:
                                bootstrap_result = await asyncio.to_thread(bootstrap.launch_osu, gameserver, mods)
                                if bootstrap_result != 9:
                                    isgd = False
                                    break
                    else:
                        playbtn.setProperty("text", "LAUNCHING")
                        bootstrap_result = await asyncio.to_thread(bootstrap.setup_osu_lazer)
                    playbtn.setProperty("enabled", True)
                    playbtn.setProperty("text", "LAUNCH")
                    #if util.config_read_value("id10") == 1:
                    #    self.show()
            except Exception as ee:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(f"An error occured during the bootstrap process of the game.\n\n{ee}")
                msg.setWindowTitle("Error")
                msg.exec_()
                playbtn.setProperty("enabled", True)
                playbtn.setProperty("text", "LAUNCH")

        elif index == 11:
            dbg = self.root_obj.findChild(QObject, "dbg")
            dbg1 = self.root_obj.findChild(QObject, "dbg1")
            dbg2 = self.root_obj.findChild(QObject, "dbg2")
            if status == 0:
                dbg.setProperty("visible", False)
                dbg1.setProperty("visible", False)
                dbg2.setProperty("visible", False)
            else:
                dbg.setProperty("visible", True)
                dbg1.setProperty("visible", True)
                dbg2.setProperty("visible", True)

            util.config_set_value("id11", status)
        elif index == 111:
            sel = self.root_obj.findChild(QObject, "serversel")
            inp = self.root_obj.findChild(QObject, "serverinp")
            if status == 0:
                inp.setProperty("visible", False)
                sel.setProperty("visible", True)
            else:
                inp.setProperty("visible", True)
                sel.setProperty("visible", False)

            util.config_set_value("id111", status)
        elif index == 10:
            util.config_set_value("id10", status)
        elif index == 0:
            util.config_set_value("id0", status)
        elif index == 1:
            util.config_set_value("id1", status)
        elif index == 6969:
            configdata = util.get_configdata()
            subprocess.Popen(f'explorer "{os.path.join(configdata["m1pppath"], "mods")}"')
        elif index == 990:
            webbrowser.open("https://github.com/M1PPosu")
        elif index == 991:
            webbrowser.open("https://dsc.gg/m1ppand4ayo")
        elif index == 420:
            webbrowser.open(self.newslink)

if __name__ == "__main__":
    willrun = True
    if len(sys.argv) > 1 and sys.argv[1].lower() == "uninstall":
        willrun = False
        uninstall()
        sys.exit(0)
    if os.path.exists(UNINSTALL_SIGNAL):
        willrun = False
        uninstall()
        sys.exit(0)

    if willrun:
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(util.resource_path("icon.png")))
        loop = qasync.QEventLoop(app)
        engine = QQmlApplicationEngine()
        window = MainWindow()
        engine.rootContext().setContextProperty("window", window)
        engine.load(util.resource_path("gui.qml"))

        if engine.rootObjects():
            window.set_qml_root(engine.rootObjects()[0])

        with loop:
            loop.run_forever()
