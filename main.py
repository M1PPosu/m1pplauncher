import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import webbrowser

import psutil
import requests

import bootstrap
import m1pp_logger
import util
from discord_presence import DiscordPresence

from PySide6.QtCore import QObject, Property, QUrl, QtMsgType, Signal, Slot, qInstallMessageHandler
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

os.environ.setdefault("QT_API", "pyside6")
import qasync

LOCAL_VERSION = "v4b"
DISCORD_CLIENT_ID = "1460103326560682137"
LOCALAPPDATA = os.environ.get("LOCALAPPDATA") or ""

_log = logging.getLogger("launcher")


def _qobj_text(obj: QObject) -> str:
    if obj is None:
        return ""

    value = obj.property("text")
    if isinstance(value, str) and value.strip():
        return value.strip()

    value = obj.property("displayText")
    if isinstance(value, str) and value.strip():
        return value.strip()

    return ""


def _sanitize_host(value: str) -> str:
    s = (value or "").strip()
    if not s:
        return ""

    return s.replace("https://", "", 1).replace("http://", "", 1).rstrip("/")


def _show_error(title: str, body: str) -> None:
    QMessageBox.critical(None, title, body)


def _read_json(path: str) -> dict:
    if not path or not os.path.isfile(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data if isinstance(data, dict) else {}


def _read_installdata_safe() -> dict:
    paths = [
        os.path.join(util.get_app_path(), "installdata.json"),
        os.path.join(LOCALAPPDATA, "M1PPLauncher", "installdata.json") if LOCALAPPDATA else "",
    ]

    for path in paths:
        try:
            data = _read_json(path)
        except (OSError, json.JSONDecodeError) as e:
            _log.warning("Failed reading installdata.json at %s: %s", path, e)
            continue

        if data:
            data.setdefault("m1pppath", "")
            data.setdefault("osupath", "")
            return data

    return {"m1pppath": "", "osupath": ""}


def _mods_path() -> str:
    path = os.path.join(util.get_app_path(), "mods")
    os.makedirs(path, exist_ok=True)
    return path


def _valid_osu_path(path: str) -> bool:
    return bool(path) and os.path.isfile(os.path.join(path, "osu!.exe"))


def _open_url(url: str) -> None:
    webbrowser.open(url)


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

    def append(self, text: str) -> None:
        if text:
            self._appendRequested.emit(str(text))

    @Slot(str)
    def _append(self, text: str) -> None:
        self._text += text
        if len(self._text) > self._max:
            self._text = self._text[-self._max :]
        self.textChanged.emit()


class TeeStream:
    def __init__(self, console: ConsoleOut, original):
        self._console = console
        self._original = original

    def write(self, text):
        if self._original:
            try:
                self._original.write(text)
            except Exception:
                pass
        self._console.append(text)

    def flush(self):
        if self._original:
            try:
                self._original.flush()
            except Exception:
                pass


class ConsoleLogHandler(logging.Handler):
    def __init__(self, console: ConsoleOut):
        super().__init__(level=logging.DEBUG)
        self._console = console
        self.setFormatter(logging.Formatter("(%(asctime)s) [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"))

    def emit(self, record):
        self._console.append(self.format(record) + "\n")


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

    def set_qml_root(self, root):
        self.root_obj = root

        try:
            self.updatenews()
        except requests.RequestException as e:
            _log.warning("News update error: %s", e)
            self.isonline += " (Disconnected)"
        except (OSError, json.JSONDecodeError) as e:
            _log.warning("News parse error: %s", e)
            self.isonline += " (Disconnected)"

        settings, id0, id1, id11, id111 = util.config_setup()

        for name, value in settings.items():
            obj = self.root_obj.findChild(QObject, name)
            if obj is not None:
                obj.setProperty("checked", value)

        self._apply_custom_server_visibility(id111)
        self._apply_debug_visibility(id11)
        self.update_info_stats()
        self._presence_idle()

    def _apply_custom_server_visibility(self, enabled: int) -> None:
        if self.root_obj is None:
            return

        sel = self.root_obj.findChild(QObject, "serversel")
        inp = self.root_obj.findChild(QObject, "serverinp")

        if sel is not None:
            sel.setProperty("visible", enabled == 0)
            sel.setProperty("currentIndex", 0)

        if inp is not None:
            inp.setProperty("visible", enabled != 0)

    def _apply_debug_visibility(self, enabled: int) -> None:
        if self.root_obj is None:
            return

        for name in ("dbg", "dbg1", "dbg2"):
            obj = self.root_obj.findChild(QObject, name)
            if obj is not None:
                obj.setProperty("visible", bool(enabled))

    def _presence_target(self):
        if util.config_read_value("id111") != 0 and self.root_obj is not None:
            inp = self.root_obj.findChild(QObject, "serverinp")
            server = _sanitize_host(_qobj_text(inp))
            if server:
                return (server, "osu", "Custom server")
            return ("Custom server", "osu", "Custom server")

        return ("M1PP Stable", "m1ppweblogo", "M1PP")

    def _presence_idle(self):
        if self.presence:
            label, img, img_text = self._presence_target()
            self.presence.set_idle(label, img, img_text)

    def _presence_launching(self):
        if self.presence:
            label, img, img_text = self._presence_target()
            self.presence.set_launching(label, img, img_text)

    def _presence_playing(self):
        if self.presence:
            label, img, img_text = self._presence_target()
            self.presence.set_playing(label, img, img_text)

    def updatenews(self):
        recv = requests.get("https://4ayo.ovh/m1pposu/news/news.json", timeout=2).json()
        remote_version = str(recv.get("current_version") or "").strip()

        if not remote_version.lower().startswith("v"):
            return

        if remote_version.lower() == LOCAL_VERSION:
            return

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(f"New version of M1PP Launcher has been released. Download it now? ({remote_version})")
        msg.setWindowTitle("Update available")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)

        if msg.exec() != QMessageBox.Yes:
            return

        updater_src = util.resource_path("m1ppupdater.exe")
        if not os.path.isfile(updater_src):
            raise FileNotFoundError(updater_src)

        temp_dir = tempfile.mkdtemp(prefix="m1pp_updater_")
        updater_dst = os.path.join(temp_dir, "m1ppupdater.exe")
        shutil.copy2(updater_src, updater_dst)

        target_dir = util.get_app_path()
        subprocess.Popen([updater_dst, target_dir], cwd=temp_dir)
        QApplication.instance().quit()

    def update_info_stats(self):
        if self.root_obj is None:
            return

        modsenabled = 0
        customstatus = "Enabled" if util.config_read_value("id111") != 0 else "Disabled"

        if util.config_read_value("id0") == 1:
            modsenabled += 1
        if util.config_read_value("id1") == 1:
            modsenabled += 1

        try:
            for file_name in os.listdir(_mods_path()):
                if file_name.lower().endswith(".mmod"):
                    modsenabled += 1
        except OSError as e:
            _log.warning("Failed reading mods folder: %s", e)

        statusbox = self.root_obj.findChild(QObject, "dbg")
        if statusbox is not None:
            statusbox.setProperty(
                "text",
                f"\n\nClient channel: Stable"
                f"\nLoaded mods: {modsenabled}"
                f"\nConnection: {self.isonline}"
                f"\nCustom server: {customstatus}",
            )

    def _selected_server(self) -> str:
        if util.config_read_value("id111") == 0:
            return "m1pposu.dev"

        inp = self.root_obj.findChild(QObject, "serverinp") if self.root_obj is not None else None
        server = _sanitize_host(_qobj_text(inp))

        if not server or "." not in server or " " in server:
            raise RuntimeError("Invalid custom server domain.")

        if server.lower() in ("ppy.sh", "osu.ppy.sh"):
            raise RuntimeError("Official Bancho servers are not supported by this launcher.")

        return server

    async def _launch_stable(self):
        playbtn = self.root_obj.findChild(QObject, "playbtn") if self.root_obj is not None else None

        try:
            if playbtn is not None:
                playbtn.setProperty("enabled", False)
                playbtn.setProperty("text", "LOADING MODS")

            data = _read_installdata_safe()
            if not _valid_osu_path(str(data.get("osupath") or "")) and not _valid_osu_path(str(data.get("m1pppath") or "")):
                raise RuntimeError("Could not find osu!.exe. Re-run setup and select your osu!stable folder.")

            gameserver = self._selected_server()
            _log.info("Bootstrapping stable client. server=%s", gameserver)

            dismods = []
            if util.config_read_value("id0") == 0:
                dismods.append("RelaxPatcher")
            if util.config_read_value("id1") == 0:
                dismods.append("tosu")

            mods = await asyncio.to_thread(bootstrap.load_mods, dismods, "stable")
            if isinstance(mods, list):
                raise RuntimeError(f"Mod loader failed for {mods[1]}: {mods[0]}")

            if playbtn is not None:
                playbtn.setProperty("text", "LAUNCHING")

            self._presence_playing()
            result = await asyncio.to_thread(bootstrap.launch_osu, gameserver, mods)

            while result == 9:
                result = await asyncio.to_thread(bootstrap.launch_osu, gameserver, mods)

            if result == 1:
                raise RuntimeError("Could not find osu!.exe. Re-run setup and select your osu!stable folder.")

        finally:
            if playbtn is not None:
                playbtn.setProperty("enabled", True)
                playbtn.setProperty("text", "LAUNCH")
            self._presence_idle()

    @qasync.asyncSlot(int, int)
    async def execguifn(self, index, status):
        _log.info("execguifn index=%s status=%s", index, status)

        if index == 880811:
            self.update_info_stats()
            self._presence_idle()
            return

        if index == 2137:
            self._presence_launching()
            try:
                await self._launch_stable()
            except Exception as e:
                _log.exception("Bootstrap error: %s", e)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(f"An error occurred during launch.\n\n{e}")
                msg.setWindowTitle("Error")
                msg.exec()
                self._presence_idle()
            return

        if index == 111:
            util.config_set_value("id111", status)
            self._apply_custom_server_visibility(status)
            self.update_info_stats()
            self._presence_idle()
            return

        if index == 11:
            util.config_set_value("id11", status)
            self._apply_debug_visibility(status)
            return

        if index == 0:
            util.config_set_value("id0", status)
            self.update_info_stats()
            return

        if index == 1:
            util.config_set_value("id1", status)
            self.update_info_stats()
            return

        if index == 6969:
            subprocess.Popen(["explorer", _mods_path()])
            return

        if index == 990:
            _open_url("https://github.com/M1PPosu/m1pplauncher")
            return

        if index == 991:
            _open_url("https://discord.gg/RXQFFZx4ac")
            return


def _ensure_standard_streams() -> None:
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8", errors="ignore")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8", errors="ignore")


def _install_qt_message_handler(console: ConsoleOut) -> None:
    def qt_msg_handler(mode, context, message):
        level = {
            QtMsgType.QtDebugMsg: "DEBUG",
            QtMsgType.QtWarningMsg: "WARN",
            QtMsgType.QtCriticalMsg: "CRITICAL",
            QtMsgType.QtFatalMsg: "FATAL",
        }.get(mode, "INFO")

        console.append(f"[Qt {level}] {message}\n")

    qInstallMessageHandler(qt_msg_handler)


def main() -> int:
    global _log

    _ensure_standard_streams()

    m1pp_logger.setup("launcher")
    _log = m1pp_logger.get_logger("launcher")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(util.resource_path("icon.png")))

    console = ConsoleOut()
    _log.addHandler(ConsoleLogHandler(console))

    sys.stdout = TeeStream(console, sys.stdout)
    sys.stderr = TeeStream(console, sys.stderr)

    _install_qt_message_handler(console)

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    engine = QQmlApplicationEngine()
    window = MainWindow()

    engine.rootContext().setContextProperty("window", window)
    engine.rootContext().setContextProperty("consoleOut", console)

    settings, id0, id1, id11, id111 = util.config_setup()
    ctx = engine.rootContext()
    ctx.setContextProperty("switch_patcher", bool(int(id0)))
    ctx.setContextProperty("switch_tosu", bool(int(id1)))
    ctx.setContextProperty("switch_launchinfo", bool(int(id11)))
    ctx.setContextProperty("switch_hidelauncher", bool(int(id111)))

    qml_path = util.resource_path("gui.qml")
    engine.load(QUrl.fromLocalFile(qml_path))

    if not engine.rootObjects():
        _show_error("Failed to load gui.qml", f"QML path:\n{qml_path}")
        return 1

    window.set_qml_root(engine.rootObjects()[0])

    window.presence = DiscordPresence.create(DISCORD_CLIENT_ID, _log)
    if window.presence:
        app.aboutToQuit.connect(window.presence.close)
        window._presence_idle()

    with loop:
        loop.run_forever()

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        _log.exception("Fatal startup crash: %s", e)
        try:
            _show_error("Launcher crash", str(e))
        finally:
            raise
        
# Could split this into 3 other files if REALLY needed. 