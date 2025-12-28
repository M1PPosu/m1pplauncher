import sys
import os
import ctypes
import time
import datetime
import asyncio
import aiohttp
import aiofiles
import subprocess
import shutil
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtQml import QQmlApplicationEngine
import qasync
import psutil

# for the sake of transparency, this is basically the installer stripped down, with also whatever chatgpt shit out. 

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

errpath = os.path.join(
    os.environ["LOCALAPPDATA"],
    f"m1ppupdatelog-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
)

def setuplog(level, text):
    prefix = ["INFO", "WARN", "ERROR", "CRITICAL"][level]
    with open(errpath, "a", encoding="utf-8") as f:
        f.write(f"[{prefix}] {text}\n")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

class Updater(QObject):
    progressChanged = Signal(float)
    statusChanged = Signal(str)
    finished = Signal(bool)

    def __init__(self):
        super().__init__()
        self.target_dir = sys.argv[1]

    @qasync.asyncSlot()
    async def start(self):
        url = "https://4ayo.ovh/m1pposu/files/launcher/latest/m1pplauncher.exe"
        target = os.path.join(self.target_dir, "m1pplauncher.exe")
        tmp = target + ".tmp"
        processes = ["tosu.exe", "m1pplauncher.exe"]
        for process in processes:
            for proc in psutil.process_iter():
                if proc.name() == process:
                    proc.kill()
        self.statusChanged.emit("Downloading update…")
        setuplog(0, f"Downloading to {target}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    total = int(resp.headers.get("Content-Length", 0))
                    downloaded = 0

                    async with aiofiles.open(tmp, "wb") as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            await f.write(chunk)
                            downloaded += len(chunk)
                            percent = (downloaded / total) * 100
                            self.progressChanged.emit(percent)

            os.replace(tmp, target)
            self.statusChanged.emit("Update complete")
            await asyncio.sleep(1)
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

if __name__ == "__main__":
    setuplog(0, "Updater started")

    if len(sys.argv) > 1 and sys.argv[1].lower() == "finishuninstall":
        time.sleep(2)
        subprocess.call(['taskkill', '/F', '/T', '/PID',  sys.argv[2]])
        mipath = sys.argv[3]
        shutil.rmtree(mipath, ignore_errors=True)
        ctypes.windll.user32.MessageBoxW(0, "M1PP Launcher has been uninstalled.", "Success", 4160)

    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)

    if len(sys.argv) < 2:
        QMessageBox.critical(None, "Updater error", "No install path provided. Most likely a bug.")
        sys.exit(1)

    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    engine = QQmlApplicationEngine()

    updater = Updater()
    engine.rootContext().setContextProperty("updater", updater)

    engine.load(resource_path("gui.qml"))

    if not engine.rootObjects():
        sys.exit(1)

    with loop:
        updater.start()
        loop.run_forever()
