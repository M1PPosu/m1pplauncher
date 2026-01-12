import sys
import os
import shutil
import webbrowser
import ctypes
import subprocess
import winreg
import asyncio

import qasync
import crossinstallutil

import m1pp_logger
m1pp_logger.setup("installer")

from PySide6.QtCore import QObject, QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PySide6.QtQml import QQmlApplicationEngine


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception as e:
        crossinstallutil.setuplog(2, f"is_admin() failed: {e}")
        return False


def _qobj_get_text(obj: QObject) -> str:
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


def _show_error(parent, title: str, body: str):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(body)
    msg.exec()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_obj: QObject | None = None
        self.engine: QQmlApplicationEngine | None = None
        self.step = 1

        self.osupath = crossinstallutil.check_osu_install_path()
        crossinstallutil.setuplog(0, f"Detected osu! path: {self.osupath}")

        self.manualpath = (self.osupath == 2)
        self.m1pppath = ""

    def closeEvent(self, event):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to interrupt the setup?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirmation == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def _set_step_visible(self, step: int):
        nextstep = self.root_obj.findChild(QObject, f"step{step}") if self.root_obj is not None else None
        prevstep = self.root_obj.findChild(QObject, f"step{self.step}") if self.root_obj is not None else None

        if prevstep is not None:
            prevstep.setProperty("visible", False)
        if nextstep is not None:
            nextstep.setProperty("visible", True)

        crossinstallutil.setuplog(0, f"Step changed, {self.step} -> {step}")
        self.step = step

    @qasync.asyncSlot(int)
    async def display_step(self, step: int):
        crossinstallutil.setuplog(0, f"display_step() called with step={step}, current step={self.step}")

        if self.root_obj is None:
            return

        if step == 3:
            p = crossinstallutil.check_osu_install_path()
            if isinstance(p, str) and p:
                self.osupath = p
                self.manualpath = False
                step = 4
            elif p == 2:
                self.manualpath = True
                _show_error(
                    self,
                    "Error",
                    "We could not resolve a valid osu! stable path. Please select your osu! stable installation folder.",
                )
                step = 999

        elif step == 5:
            foldersel = self.root_obj.findChild(QObject, "pathsel")
            folder = _qobj_get_text(foldersel)

            if not folder:
                _show_error(self, "Error", "Please select a valid installation directory.")
                return

            try:
                os.makedirs(folder, exist_ok=True)
            except Exception:
                pass

            if not os.access(folder, os.W_OK):
                _show_error(
                    self,
                    "Error",
                    "The path you selected is invalid or inaccessible. Please select a directory the installer can access, or run the installer with administrator privileges.",
                )
                return

            try:
                if os.listdir(folder):
                    _show_error(self, "Error", "The folder you selected is not empty.")
                    return
            except Exception:
                _show_error(self, "Error", "The folder you selected is invalid or inaccessible.")
                return

            try:
                os.makedirs(os.path.join(folder, "mods"), exist_ok=True)
            except Exception:
                pass

            self.m1pppath = folder
            textsum = self.root_obj.findChild(QObject, "summarytext")
            if textsum is not None:
                textsum.setProperty("text", f"osu! path: {self.osupath}\nInstallation path: {self.m1pppath}")

        elif step == 9990:
            foldersel = self.root_obj.findChild(QObject, "opathsel")
            folder = _qobj_get_text(foldersel)

            if not folder:
                _show_error(self, "Error", "Please select a valid osu!stable installation directory.")
                return

            if not os.access(folder, os.R_OK):
                _show_error(self, "Error", "The path you selected is inaccessible.")
                return

            if not os.path.isfile(os.path.join(folder, "osu!auth.dll")):
                _show_error(self, "Error", "The path you selected does not contain an osu! stable installation.")
                return

            self.osupath = folder
            self.manualpath = False
            step = 4

        elif step == 33:
            if self.osupath:
                step = 2

        elif step == 93:
            webbrowser.open("https://www.gnu.org/licenses/gpl-3.0.txt")
            return

        elif step == 2942:
            webbrowser.open("https://m1.ppy.sh/r/osu!install.exe")
            return

        elif step == 8901:
            try:
                log_dir = os.path.dirname(crossinstallutil.errpath)
                subprocess.Popen(f'explorer "{log_dir}"')
            except Exception as e:
                crossinstallutil.setuplog(2, f"Failed to open logs folder: {e}")
            return

        elif step == 8:
            QApplication.instance().quit()
            return

        elif step == 78:
            p = crossinstallutil.check_osu_install_path()
            self.osupath = p
            crossinstallutil.setuplog(0, f"Re-detected osu! path: {self.osupath}")

            if p is False:
                _show_error(self, "Error", "osu!stable is not installed yet.")
                return
            if p == 2:
                _show_error(self, "Error", "We could not resolve a valid osu! stable path. Please select it manually.")
                step = 999
            elif isinstance(p, str) and p:
                self.manualpath = False
                step = 4

        elif step == 79:
            folder = str(QFileDialog.getExistingDirectory(self, "Select M1PPLauncher install directory"))
            textinput = self.root_obj.findChild(QObject, "pathsel")
            if folder and textinput is not None:
                textinput.setProperty("text", folder)
            return

        elif step == 99979:
            folder = str(QFileDialog.getExistingDirectory(self, "Select osu! install directory"))
            textinput = self.root_obj.findChild(QObject, "opathsel")
            if folder and textinput is not None:
                textinput.setProperty("text", folder)
            return

        self._set_step_visible(step)

        if step == 4:
            textinput = self.root_obj.findChild(QObject, "pathsel")
            default = os.path.join(os.getenv("LOCALAPPDATA") or "", "osu!m1pp-reborn")
            if textinput is not None:
                textinput.setProperty("text", default)

        elif step == 89:
            textinput = self.root_obj.findChild(QObject, "errpath")
            if textinput is not None:
                textinput.setProperty(
                    "text",
                    "An error has occured during the installation.\nSetup logs are located at " + crossinstallutil.errpath,
                )

        elif step == 6:
            curtext = self.root_obj.findChild(QObject, "curtext")
            curbar = self.root_obj.findChild(QObject, "curbar")

            ok = await crossinstallutil.install_osu(self.m1pppath, self.osupath, curbar, curtext)
            if ok:
                try:
                    for name in ("gui.qml", "icon.png", "fade.png", "unknown.png"):
                        src = resource_path(name)
                        dst = os.path.join(self.m1pppath, name)
                        if os.path.isfile(src):
                            shutil.copy2(src, dst)

                    slides_src = resource_path("slides")
                    slides_dst = os.path.join(self.m1pppath, "slides")
                    if os.path.isdir(slides_src):
                        if os.path.isdir(slides_dst):
                            shutil.rmtree(slides_dst, ignore_errors=True)
                        shutil.copytree(slides_src, slides_dst)
                except Exception as e:
                    crossinstallutil.setuplog(2, f"Failed copying launcher UI assets: {e}")

                self._set_step_visible(7)
            else:
                self._set_step_visible(89)


if __name__ == "__main__":
    crossinstallutil.setuplog(0, "Installer started.")

    if not is_admin():
        if getattr(sys, "frozen", False):
            exe = sys.executable
            params = subprocess.list2cmdline(sys.argv[1:])
        else:
            exe = sys.executable
            params = subprocess.list2cmdline([os.path.abspath(__file__), *sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
        raise SystemExit

    app = QApplication(sys.argv)

    already_installed = False
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        k = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\M1PPLauncher")
        winreg.CloseKey(k)
        already_installed = True
    except Exception:
        already_installed = False

    if already_installed:
        _show_error(None, "Error", "M1PP Launcher is already installed!")
        raise SystemExit

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    engine = QQmlApplicationEngine()
    window = MainWindow()

    engine.rootContext().setContextProperty("window", window)
    engine.load(QUrl.fromLocalFile(resource_path("steps.qml")))

    if engine.rootObjects():
        window.root_obj = engine.rootObjects()[0]

    with loop:
        loop.run_forever()
