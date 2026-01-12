import sys
import os
import json
import time
import ctypes
import shutil
import tempfile
import asyncio
import logging
import subprocess
import webbrowser
import winreg

import psutil
import requests
import qasync
import winshell

import util
import bootstrap
import m1pp_logger
from discord_presence import DiscordPresence

from ctypes import wintypes
from PySide6.QtGui import QIcon
from PySide6.QtCore import (
    QObject,
    QUrl,
    QTimer,
    Signal,
    Property,
    Slot,
    QtMsgType,
    qInstallMessageHandler,
)
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtQml import QQmlApplicationEngine

LOCAL_VERSION = "v4B"
DISCORD_CLIENT_ID = "1460103326560682137"

m1pp_logger.setup("launcher")
_log = m1pp_logger.get_logger("launcher")

LOCALAPPDATA = os.environ.get("LOCALAPPDATA") or ""
UNINSTALL_SIGNAL = (
    os.path.join(LOCALAPPDATA, "uninstall_pending.txt")
    if LOCALAPPDATA
    else os.path.join(tempfile.gettempdir(), "m1pp_uninstall_pending.txt")
)

def _qobj_text(obj: QObject) -> str:
    if obj is None:
        return ""
    try:
        v = obj.property("text")
        if isinstance(v, str) and v.strip():
            return v.strip()
    except Exception:
        pass
    try:
        v = obj.property("displayText")
        if isinstance(v, str) and v.strip():
            return v.strip()
    except Exception:
        pass
    return ""

def _sanitize_host(value: str) -> str:
    s = (value or "").strip()
    if not s:
        return ""
    s = s.replace("https://", "", 1).replace("http://", "", 1).strip().rstrip("/")
    return s


def _show_error(title: str, body: str):
    try:
        QMessageBox.critical(None, title, body)
    except Exception:
        pass

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _read_installdata_safe() -> dict:
    candidates = [
        os.path.join(util.get_app_path(), "installdata.json"),
        util.resource_path("installdata.json"),
        os.path.join(LOCALAPPDATA, "M1PPLauncher", "installdata.json") if LOCALAPPDATA else "",
    ]

    for path in candidates:
        try:
            if path and os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass

    return {}


def uninstall():
    if not is_admin():
        try:
            with open(UNINSTALL_SIGNAL, "w", encoding="utf-8") as f:
                f.write("uninstall")
        except Exception as e:
            _log.warning("Failed to write uninstall signal: %s", e)

        try:
            if getattr(sys, "frozen", False):
                exe = sys.executable
                params = ""
            else:
                exe = sys.executable
                params = subprocess.list2cmdline([os.path.abspath(__file__)])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
        except Exception as e:
            _log.error("Failed to elevate: %s", e)

        sys.exit(0)

    try:
        data = _read_installdata_safe()
        mipath = data.get("m1pppath")

        if not mipath or not os.path.isdir(mipath):
            _log.warning("Uninstall aborted: m1pppath missing/invalid in installdata.json")
            try:
                os.remove(UNINSTALL_SIGNAL)
            except Exception:
                pass
            sys.exit(0)

        for proc in psutil.process_iter(attrs=["name"]):
            try:
                if (proc.info.get("name") or "").lower() == "tosu.exe":
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.DeleteFileW.argtypes = [wintypes.LPCWSTR]
        k32.RemoveDirectoryW.argtypes = [wintypes.LPCWSTR]

        try:
            k32.DeleteFileW(os.path.join(mipath, "osu!.db"))
        except Exception:
            pass
        try:
            k32.RemoveDirectoryW(os.path.join(mipath, "Songs"))
        except Exception:
            pass
        try:
            k32.RemoveDirectoryW(os.path.join(mipath, "Skins"))
        except Exception:
            pass

        uninstall_key = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\M1PPLauncher"
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, uninstall_key)
        except FileNotFoundError:
            pass
        except OSError as e:
            _log.warning("Registry cleanup error: %s", e)

        try:
            desktop = winshell.desktop()
            startmenu = winshell.start_menu()
            for path in (
                os.path.join(desktop, "M1PP Launcher.lnk"),
                os.path.join(startmenu, "M1PP Launcher.lnk"),
            ):
                if os.path.exists(path):
                    os.remove(path)
        except Exception:
            pass

        pid = os.getpid()

        try:
            os.remove(UNINSTALL_SIGNAL)
        except Exception:
            pass

        updater_src = util.resource_path("m1ppupdater.exe")
        temp_dir = tempfile.mkdtemp(prefix="m1pp_uninstaller_")
        updater_dst = os.path.join(temp_dir, "m1ppupdater.exe")
        shutil.copy2(updater_src, updater_dst)

        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            updater_dst,
            f'finishuninstall {pid} "{mipath}"',
            None,
            1,
        )

    except Exception as e:
        _log.exception("FATAL uninstall error: %s", e)

    finally:
        try:
            os.remove(UNINSTALL_SIGNAL)
        except Exception:
            pass

    sys.exit(0)

class ConsoleOut(QObject):
    textChanged = Signal()
    _appendRequested = Signal(str)

    def __init__(self, parent=None, max_chars: int = 250000):
        super().__init__(parent)
        self._text = ""
        self._max = max_chars
        self._appendRequested.connect(self._append)

    @Property(str, notify=textChanged)
    def text(self) -> str:
        return self._text

    def append(self, s: str):
        if not s:
            return
        self._appendRequested.emit(str(s))

    @Slot(str)
    def _append(self, s: str):
        self._text += s
        if len(self._text) > self._max:
            self._text = self._text[-self._max :]
        self.textChanged.emit()


class _TeeStream:
    def __init__(self, console: ConsoleOut, original):
        self._console = console
        self._original = original

    def write(self, s):
        try:
            if self._original:
                self._original.write(s)
        except Exception:
            pass
        try:
            self._console.append(s)
        except Exception:
            pass

    def flush(self):
        try:
            if self._original:
                self._original.flush()
        except Exception:
            pass


class _ConsoleLogHandler(logging.Handler):
    def __init__(self, console: ConsoleOut):
        super().__init__(level=logging.DEBUG)
        self._console = console
        self.setFormatter(logging.Formatter("(%(asctime)s) [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"))

    def emit(self, record):
        try:
            self._console.append(self.format(record) + "\n")
        except Exception:
            pass


class LogTail(QObject):
    textChanged = Signal()

    def __init__(self, log_path: str, parent=None, max_chars: int = 200000):
        super().__init__(parent)
        self._log_path = log_path or ""
        self._text = ""
        self._pos = 0
        self._max_chars = max_chars

        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self._tick)

    @Property(str, notify=textChanged)
    def text(self) -> str:
        return self._text

    @Slot()
    def start(self):
        if not self._timer.isActive():
            self._timer.start()
        self._tick()

    def _tick(self):
        try:
            if not self._log_path or not os.path.isfile(self._log_path):
                return

            with open(self._log_path, "rb") as f:
                f.seek(0, os.SEEK_END)
                end = f.tell()
                if self._pos > end:
                    self._pos = 0
                f.seek(self._pos, os.SEEK_SET)
                chunk = f.read()
                self._pos = end

            if not chunk:
                return

            self._text += chunk.decode("utf-8", errors="replace")

            if len(self._text) > self._max_chars:
                self._text = self._text[-self._max_chars :]

            self.textChanged.emit()
        except Exception:
            return


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_obj = None
        self.isonline = "Online"
        self.presence = None

        try:
            requests.get("https://www.google.com/generate_204", timeout=2, allow_redirects=False)
        except requests.RequestException:
            self.isonline = "Offline"

    def _presence_target(self):
        custom_on = False
        try:
            custom_on = (util.config_read_value("id111") != 0)
        except Exception:
            custom_on = False

        if custom_on and self.root_obj is not None:
            inp = self.root_obj.findChild(QObject, "serverinp")
            server = _sanitize_host(_qobj_text(inp))
            if server:
                return (server, "osu", "Custom server")
            return ("Custom server", "osu", "Custom server")

        svst = self.root_obj.findChild(QObject, "serversel") if self.root_obj is not None else None
        idx = svst.property("currentIndex") if svst is not None else 0

        if idx == 1:
            return ("M1Lazer", "m1lazerlogo_1_", "M1Lazer")
        return ("M1PP Stable", "m1ppweblogo", "M1PP")

    def _presence_idle(self):
        if not self.presence:
            return
        label, img, img_text = self._presence_target()
        self.presence.set_idle(label, img, img_text)

    def _presence_launching(self):
        if not self.presence:
            return
        label, img, img_text = self._presence_target()
        self.presence.set_launching(label, img, img_text)

    def _presence_playing(self):
        if not self.presence:
            return
        label, img, img_text = self._presence_target()
        self.presence.set_playing(label, img, img_text)

    def set_qml_root(self, root):
        self.root_obj = root

        try:
            self.updatenews()
        except Exception as e:
            _log.warning("News update error: %s", e)
            self.isonline += " (Disconnected)"

        settings, id0, id1, id11, id111 = util.config_setup()

        for name, value in settings.items():
            if name == "id10":
                continue
            obj = self.root_obj.findChild(QObject, name)
            if obj is not None:
                obj.setProperty("checked", value)

        sel = self.root_obj.findChild(QObject, "serversel")
        inp = self.root_obj.findChild(QObject, "serverinp")
        if sel is not None and inp is not None:
            if id111 == 0:
                inp.setProperty("visible", False)
                sel.setProperty("visible", True)
            else:
                inp.setProperty("visible", True)
                sel.setProperty("visible", False)

        dbg = self.root_obj.findChild(QObject, "dbg")
        dbg1 = self.root_obj.findChild(QObject, "dbg1")
        dbg2 = self.root_obj.findChild(QObject, "dbg2")
        if dbg is not None and dbg1 is not None and dbg2 is not None:
            if id11 == 0:
                dbg.setProperty("visible", False)
                dbg1.setProperty("visible", False)
                dbg2.setProperty("visible", False)
            else:
                dbg.setProperty("visible", True)
                dbg1.setProperty("visible", True)
                dbg2.setProperty("visible", True)

        self.update_info_stats()
        self._presence_idle()

    def updatenews(self):
        recv = requests.get("https://4ayo.ovh/m1pposu/news/news.json", timeout=2).json()
        arrx = _read_installdata_safe()

        if recv.get("current_version", "").strip() != LOCAL_VERSION:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setText(
                f'New version of M1PPLauncher has been released! Would you like to download it? ({recv.get("current_version","")})'
            )
            msg.setWindowTitle("Update available!")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)

            if msg.exec() == QMessageBox.Yes:
                updater_src = util.resource_path("m1ppupdater.exe")
                temp_dir = tempfile.mkdtemp(prefix="m1pp_updater_")
                updater_dst = os.path.join(temp_dir, "m1ppupdater.exe")
                shutil.copy2(updater_src, updater_dst)

                m1pppath = arrx.get("m1pppath", "")
                ctypes.windll.shell32.ShellExecuteW(None, "runas", updater_dst, f'"{m1pppath}"', None, 1)
                sys.exit(0)

    def update_info_stats(self):
        if self.root_obj is None:
            return

        configdata = _read_installdata_safe()
        modsenabled = 0
        customstatus = "Disabled"

        if util.config_read_value("id0") == 1:
            modsenabled += 1
        if util.config_read_value("id1") == 1:
            modsenabled += 1

        m1pppath = configdata.get("m1pppath")
        if m1pppath and os.path.isdir(m1pppath):
            mods_dir = os.path.join(m1pppath, "mods")
            if os.path.isdir(mods_dir):
                try:
                    for ffile in os.listdir(mods_dir):
                        if ffile.lower().endswith(".mmod"):
                            modsenabled += 1
                except Exception:
                    pass

        osuplatform = "Stable"
        svst = self.root_obj.findChild(QObject, "serversel")
        if svst is not None:
            idx = svst.property("currentIndex")
            if idx == 1:
                osuplatform = "Lazer"

        if util.config_read_value("id111") != 0:
            osuplatform = "Stable"
            customstatus = "Enabled"

        statusbox = self.root_obj.findChild(QObject, "dbg")
        if statusbox is not None:
            statusbox.setProperty(
                "text",
                f"\n\nClient channel: {osuplatform}"
                f"\nLoaded mods: {modsenabled}"
                f"\nConnection: {self.isonline}"
                f"\nCustom server: {customstatus}",
            )

    @qasync.asyncSlot(int, int)
    async def execguifn(self, index, status):
        _log.info("execguifn index=%s status=%s", index, status)

        if index == 880811:
            self.update_info_stats()
            self._presence_idle()
            return

        if index == 2137:
            playbtn = None
            self._presence_launching()

            try:
                platform = "stable"
                gameserver = 10

                if util.config_read_value("id111") != 0:
                    inp = self.root_obj.findChild(QObject, "serverinp") if self.root_obj is not None else None
                    server = _sanitize_host(_qobj_text(inp))
                    if not server or "." not in server or " " in server:
                        raise Exception("Invalid custom server domain.")
                    gameserver = server
                else:
                    svst = self.root_obj.findChild(QObject, "serversel")
                    idx = svst.property("currentIndex") if svst is not None else 0
                    if idx == 1:
                        gameserver = 20
                        platform = "lazer"

                _log.info("Bootstrapping...")
                playbtn = self.root_obj.findChild(QObject, "playbtn") if self.root_obj is not None else None
                if playbtn is not None:
                    playbtn.setProperty("enabled", False)
                    playbtn.setProperty("text", "LOADING MODS")

                dismods = []
                if util.config_read_value("id0") == 0:
                    dismods.append("RelaxPatcher")
                if util.config_read_value("id1") == 0:
                    dismods.append("tosu")

                mods = await asyncio.to_thread(bootstrap.load_mods, dismods, platform)

                if isinstance(mods, list):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText(f"An error has occured during loading {mods[1]}\n\nError message: {mods[0]}")
                    msg.setWindowTitle("Mod loader error")
                    msg.exec()
                else:
                    if gameserver != 20:
                        if gameserver == 10:
                            gameserver = "m1pposu.dev"
                        if playbtn is not None:
                            playbtn.setProperty("text", "LAUNCHING")

                        self._presence_playing()
                        await asyncio.to_thread(bootstrap.launch_osu, gameserver, mods)
                    else:
                        if playbtn is not None:
                            playbtn.setProperty("text", "LAUNCHING")

                        self._presence_playing()
                        await asyncio.to_thread(bootstrap.ensure_tosu_running, mods)
                        await asyncio.to_thread(bootstrap.setup_osu_lazer)

                if playbtn is not None:
                    playbtn.setProperty("enabled", True)
                    playbtn.setProperty("text", "LAUNCH")

                self._presence_idle()

            except Exception as ee:
                _log.exception("Bootstrap error: %s", ee)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(f"An error occured during the bootstrap process of the game.\n\n{ee}")
                msg.setWindowTitle("Error")
                msg.exec()
                if playbtn is not None:
                    playbtn.setProperty("enabled", True)
                    playbtn.setProperty("text", "LAUNCH")
                self._presence_idle()

            return

        if index == 111:
            sel = self.root_obj.findChild(QObject, "serversel")
            inp = self.root_obj.findChild(QObject, "serverinp")
            if sel is not None and inp is not None:
                if status == 0:
                    inp.setProperty("visible", False)
                    sel.setProperty("visible", True)
                else:
                    inp.setProperty("visible", True)
                    sel.setProperty("visible", False)
            util.config_set_value("id111", status)
            self._presence_idle()
            return

        if index == 0:
            util.config_set_value("id0", status)
            return

        if index == 1:
            util.config_set_value("id1", status)
            return

        if index == 6969:
            configdata = _read_installdata_safe()
            m1pppath = configdata.get("m1pppath")
            if m1pppath and os.path.isdir(m1pppath):
                subprocess.Popen(f'explorer "{os.path.join(m1pppath, "mods")}"')
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Could not open mods folder because m1pppath is missing/invalid (installdata.json).")
                msg.setWindowTitle("Error")
                msg.exec()
            return

        if index == 990:
            webbrowser.open("https://github.com/M1PPosu")
            return

        if index == 991:
            webbrowser.open("https://dsc.gg/m1ppand4ayo")
            return


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1].lower() == "uninstall":
            uninstall()
            sys.exit(0)

        if os.path.exists(UNINSTALL_SIGNAL):
            uninstall()
            sys.exit(0)

        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(util.resource_path("icon.png")))

        consoleOut = ConsoleOut()
        _log.addHandler(_ConsoleLogHandler(consoleOut))

        orig_out, orig_err = sys.stdout, sys.stderr
        sys.stdout = _TeeStream(consoleOut, orig_out)
        sys.stderr = _TeeStream(consoleOut, orig_err)

        def _qt_msg_handler(mode, context, message):
            try:
                if mode == QtMsgType.QtDebugMsg:
                    lvl = "DEBUG"
                elif mode == QtMsgType.QtWarningMsg:
                    lvl = "WARN"
                elif mode == QtMsgType.QtCriticalMsg:
                    lvl = "CRITICAL"
                elif mode == QtMsgType.QtFatalMsg:
                    lvl = "FATAL"
                else:
                    lvl = "INFO"
                consoleOut.append(f"[Qt {lvl}] {message}\n")
            except Exception:
                pass

        qInstallMessageHandler(_qt_msg_handler)

        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)

        engine = QQmlApplicationEngine()
        window = MainWindow()
        engine.rootContext().setContextProperty("window", window)

        window.presence = DiscordPresence.create(DISCORD_CLIENT_ID, _log)
        if window.presence:
            try:
                app.aboutToQuit.connect(window.presence.close)
            except Exception:
                pass

        logTail = LogTail(m1pp_logger.get_log_path("launcher"))
        engine.rootContext().setContextProperty("logTail", logTail)
        engine.rootContext().setContextProperty("logtail", logTail)
        engine.rootContext().setContextProperty("consoleOut", consoleOut)

        try:
            settings_json, id0, id1, id11, id111 = util.config_setup()
        except Exception:
            settings_json, id0, id1, id11, id111 = (
                {"id0": 1, "id1": 1, "id11": 1, "id111": 0},
                1,
                1,
                1,
                0,
            )

        ctx = engine.rootContext()
        ctx.setContextProperty("switch_patcher", bool(int(id0)))
        ctx.setContextProperty("switch_tosu", bool(int(id1)))
        ctx.setContextProperty("switch_launchinfo", bool(int(id11)))
        ctx.setContextProperty("switch_hidelauncher", bool(int(id111)))

        external_qml = os.path.join(util.get_app_path(), "gui.qml")
        qml_path = external_qml if os.path.isfile(external_qml) else util.resource_path("gui.qml")

        engine.load(QUrl.fromLocalFile(qml_path))

        if engine.rootObjects():
            window.set_qml_root(engine.rootObjects()[0])
            window._presence_idle()
        else:
            _show_error("Failed to load gui.qml", f"QML path:\n{qml_path}")
            raise SystemExit(1)

        logTail.start()

        with loop:
            loop.run_forever()

    except SystemExit:
        raise
    except Exception as e:
        _log.exception("Fatal startup crash: %s", e)
        _show_error("Launcher crash", str(e))
        raise
