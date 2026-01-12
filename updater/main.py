import sys
import os
import ctypes
import time
import datetime
import asyncio
import subprocess
import shutil

import aiohttp
import aiofiles
import qasync
import psutil

from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtQml import QQmlApplicationEngine

import m1pp_logger

m1pp_logger.setup("updater")
_log = m1pp_logger.get_logger("updater")

LOG_PATH = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.abspath(".")),
    f"m1ppupdatelog-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt",
)

UPDATE_URL = "https://4ayo.ovh/m1pposu/files/launcher/v4B/m1pplauncher.exe"


def _write_fallback_log(level: int, text: str):
    try:
        prefix = ["INFO", "WARN", "ERROR", "CRITICAL"][max(0, min(level, 3))]
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{prefix}] {text}\n")
    except Exception:
        pass


def setuplog(level: int, text: str):
    try:
        if level == 1:
            _log.warning(text)
        elif level == 2:
            _log.error(text)
        elif level == 3:
            _log.critical(text)
        else:
            _log.info(text)
    except Exception:
        _write_fallback_log(level, text)


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin():
    try:
        if getattr(sys, "frozen", False):
            exe = sys.executable
            params = subprocess.list2cmdline(sys.argv[1:])
        else:
            exe = sys.executable
            params = subprocess.list2cmdline([os.path.abspath(__file__), *sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
    except Exception as e:
        setuplog(3, f"Failed to elevate: {e}")


def _kill_targets(names: set[str]):
    try:
        lowered = {n.lower() for n in names}
        for proc in psutil.process_iter(attrs=["name"]):
            name = (proc.info.get("name") or "").lower()
            if name in lowered:
                try:
                    proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
    except Exception as e:
        setuplog(2, f"Process scan/kill failed: {e}")


class Updater(QObject):
    progressChanged = Signal(float)
    statusChanged = Signal(str)
    finished = Signal(bool)

    def __init__(self, target_dir: str):
        super().__init__()
        self.target_dir = target_dir

    @qasync.asyncSlot()
    async def start(self):
        target = os.path.join(self.target_dir, "m1pplauncher.exe")
        tmp = target + ".tmp"

        _kill_targets({"tosu.exe", "m1pplauncher.exe"})

        self.statusChanged.emit("Downloading update…")
        setuplog(0, f"Downloading to {target}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(UPDATE_URL) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"HTTP {resp.status}")

                    total = int(resp.headers.get("Content-Length") or 0)
                    downloaded = 0

                    async with aiofiles.open(tmp, "wb") as f:
                        async for chunk in resp.content.iter_chunked(16384):
                            if not chunk:
                                continue
                            await f.write(chunk)
                            downloaded += len(chunk)

                            if total > 0:
                                percent = (downloaded / total) * 100.0
                                if percent > 100.0:
                                    percent = 100.0
                                self.progressChanged.emit(percent)

            self.progressChanged.emit(100.0)

            replaced = False
            last_err = None
            for _ in range(25):
                try:
                    os.replace(tmp, target)
                    replaced = True
                    break
                except Exception as e:
                    last_err = e
                    await asyncio.sleep(0.15)

            if not replaced:
                raise RuntimeError(f"os.replace failed: {last_err}")

            self.statusChanged.emit("Update complete")
            await asyncio.sleep(0.6)

            try:
                subprocess.Popen([target], cwd=os.path.dirname(target))
                setuplog(0, f"Launched {target}")
            except Exception as e:
                setuplog(2, f"Failed to launch app: {e}")

            self.finished.emit(True)

        except Exception as e:
            setuplog(3, f"Update failed: {e}")
            self.statusChanged.emit("Update failed")
            self.finished.emit(False)

        finally:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass


def _finish_uninstall():
    time.sleep(2)
    subprocess.call(["taskkill", "/F", "/T", "/PID", sys.argv[2]])
    mipath = sys.argv[3]
    shutil.rmtree(mipath, ignore_errors=True)
    ctypes.windll.user32.MessageBoxW(0, "M1PP Launcher has been uninstalled.", "Success", 4160)
    sys.exit(0)


if __name__ == "__main__":
    setuplog(0, "Updater started")

    if len(sys.argv) > 1 and sys.argv[1].lower() == "finishuninstall":
        if len(sys.argv) < 4:
            QMessageBox.critical(None, "Updater error", "Invalid uninstall arguments.")
            sys.exit(1)
        _finish_uninstall()

    if len(sys.argv) < 2:
        QMessageBox.critical(None, "Updater error", "No install path provided. Most likely a bug.")
        sys.exit(1)

    if not is_admin():
        relaunch_as_admin()
        sys.exit(0)

    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        QMessageBox.critical(None, "Updater error", "Install path is invalid. Most likely a bug.")
        sys.exit(1)

    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    engine = QQmlApplicationEngine()

    updater = Updater(target_dir)
    engine.rootContext().setContextProperty("updater", updater)

    engine.load(QUrl.fromLocalFile(resource_path("gui.qml")))
    if not engine.rootObjects():
        sys.exit(1)

    with loop:
        loop.create_task(updater.start())
        loop.run_forever()
