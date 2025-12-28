import sys
import os
import webbrowser
import PySide6.QtAsyncio as QtAsyncio
import qasync
import crossinstallutil
import atexit
import winreg
import sys
import ctypes
from PySide6.QtCore import QObject, Slot, QUrl, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PySide6.QtQml import QQmlApplicationEngine

cleanup = False

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def is_admin():
    try:
        admin = ctypes.windll.shell32.IsUserAnAdmin()
        crossinstallutil.setuplog(0, f"is_admin() {admin}")
        return admin
    except Exception as e:
        crossinstallutil.setuplog(2, f"is_admin() failed: {e}")
        return False


def cleanup_setup(m1pppath, osupath):
    global cleanup
    crossinstallutil.setuplog(0, f"Running cleanup_setup({m1pppath}, {osupath}) cleanup={cleanup}")
    if cleanup:
        pass


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_obj = None
        self.engine = None
        self.step = 1
        self.manualpath = False

        self.osupath = crossinstallutil.check_osu_install_path()
        crossinstallutil.setuplog(0, f"Detected osu! path: {self.osupath}")
        if self.osupath == 2:
            self.manualpath = True

        self.m1pppath = ""
        
    def run(self):
        sys.exit(QApplication.instance().exec())

    def closeEvent(self, event):
        crossinstallutil.setuplog(1, "User attempted to close setup window.")
        confirmation = QMessageBox.question(
            self, "Confirmation",
            "Are you sure you want to interrupt the setup?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            crossinstallutil.setuplog(1, "User confirmed closing setup.")
            event.accept()
        else:
            crossinstallutil.setuplog(0, "User canceled closing dialog.")
            event.ignore()

    @qasync.asyncSlot(int)
    async def display_step(self, step):
        crossinstallutil.setuplog(0, f"display_step() called with step={step}, current step={self.step}")

        # step logic
        if step == 3:
            if not self.manualpath:
                if crossinstallutil.check_osu_install_path():
                    crossinstallutil.setuplog(0, "Skipping osu! path selection (auto-detected).")
                    step = 4
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(
                    "We could not resolve a valid osu! stable path, please select your osu! stable installation folder."
                )
                msg.setWindowTitle("Error")
                msg.exec_()
                step = 999

        elif step == 5:
            foldersel = self.root_obj.findChild(QObject, "pathsel")
            folder = foldersel.property("displayText")
            crossinstallutil.setuplog(0, f"User selected install folder: {folder}")

            try:
                os.makedirs(folder)
                crossinstallutil.setuplog(0, f"Created directory: {folder}")
            except:
                crossinstallutil.setuplog(1, f"Directory already exists or cannot be created: {folder}")

            if not os.access(folder, os.W_OK):
                crossinstallutil.setuplog(2, f"Directory not writable: {folder}")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(
                    "The path you selected is invalid or inaccessible. Please select a directory "
                    "that the installer can access, or run the installer with administrator privileges."
                )
                msg.setWindowTitle("Error")
                msg.exec_()
                return

            if len(os.listdir(folder)) != 0:
                crossinstallutil.setuplog(2, f"Directory not empty: {folder}")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("The folder you selected is not empty")
                msg.setWindowTitle("Error")
                msg.exec_()
                return

            os.makedirs(os.path.join(folder, "mods"))
            crossinstallutil.setuplog(0, f"Created mods folder: {os.path.join(folder, 'mods')}")

            self.m1pppath = folder
            crossinstallutil.setuplog(0, f"Installation path set to: {self.m1pppath}")

            textsum = self.root_obj.findChild(QObject, "summarytext")
            textsum.setProperty("text", f"osu! path: {self.osupath}\nInstallation path: {self.m1pppath}")
        elif step == 9990:
            foldersel = self.root_obj.findChild(QObject, "opathsel")
            folder = foldersel.property("displayText")
            crossinstallutil.setuplog(0, f"User selected game folder: {folder}")

            if not os.access(folder, os.R_OK):
                crossinstallutil.setuplog(2, f"Directory not readable: {folder}")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(
                    "The path you selected is inaccessible."
                    "Please run the installer with administrator privileges."
                )
                msg.setWindowTitle("Error")
                msg.exec_()
                return

            if not os.path.isfile(folder + "\\osu!auth.dll"):
                crossinstallutil.setuplog(2, f"Directory invalid: {folder}")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(
                    "The path you selected does not contain an osu! stable installation."
                )
                msg.setWindowTitle("Error")
                msg.exec_()
                return
            
            self.osupath = folder
            step = 4
            self.aaaaaa = False

        elif step == 33:
            if self.osupath:
                crossinstallutil.setuplog(0, "Skipped osu! path dialog (auto-detected earlier)")
                step = 2

        elif step == 93:
            crossinstallutil.setuplog(0, "Opening GPLv3 link")
            webbrowser.open("https://www.gnu.org/licenses/gpl-3.0.txt")
            return

        elif step == 2942:
            crossinstallutil.setuplog(0, "Opening official osu! installer link")
            webbrowser.open("https://m1.ppy.sh/r/osu!install.exe")
            return

        elif step == 8:
            crossinstallutil.setuplog(0, "User finished setup, quitting.")
            QApplication.instance().quit()

        elif step == 78:
            self.osupath = crossinstallutil.check_osu_install_path()
            crossinstallutil.setuplog(0, f"Re-detected osu! path: {self.osupath}")

            if self.osupath == False:
                crossinstallutil.setuplog(2, "osu!stable not found while rechecking.")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("osu!stable is not installed yet.")
                msg.setWindowTitle("Error")
                msg.exec_()
                return
            step = 4

        elif step == 79:
            folder = str(QFileDialog.getExistingDirectory(self, "Select M1PPLauncher install directory"))
            crossinstallutil.setuplog(0, f"Manual folder selection returned: {folder}")

            textinput = self.root_obj.findChild(QObject, "pathsel")
            if folder != "":
                textinput.setProperty("text", folder)
            return
        elif step == 99979:
            folder = str(QFileDialog.getExistingDirectory(self, "Select osu! install directory"))
            crossinstallutil.setuplog(0, f"Manual game folder selection returned: {folder}")

            textinput = self.root_obj.findChild(QObject, "opathsel")
            if folder != "":
                textinput.setProperty("text", folder)
            return

        nextstep = self.root_obj.findChild(QObject, f"step{step}")
        prevstep = self.root_obj.findChild(QObject, f"step{self.step}")

        if prevstep:
            prevstep.setProperty("visible", False)
        if nextstep:
            nextstep.setProperty("visible", True)

        crossinstallutil.setuplog(0, f"Step changed, {self.step} -> {step}")
        self.step = step

        if step == 4:
            textinput = self.root_obj.findChild(QObject, "pathsel")
            default = os.environ["LOCALAPPDATA"] + r"\osu!m1pp-reborn"
            textinput.setProperty("text", default)
            crossinstallutil.setuplog(0, f"Default install path set: {default}")

        elif step == 89:
            textinput = self.root_obj.findChild(QObject, "errpath")
            textinput.setProperty("text", "An error has occured during the installation.\nSetup logs are located at " + crossinstallutil.errpath)
            crossinstallutil.setuplog(1, "Installer failed, displaying error page.")

        elif step == 6:
            crossinstallutil.setuplog(0, "Beginning installation async step")
            curtext = self.root_obj.findChild(QObject, "curtext")
            curbar = self.root_obj.findChild(QObject, "curbar")

            global cleanup
            cleanup = True
            atexit.register(cleanup_setup, self.m1pppath, self.osupath)
            crossinstallutil.setuplog(0, f"Cleanup registered with atexit (path={self.m1pppath})")

            if await crossinstallutil.install_osu(self.m1pppath, self.osupath, curbar, curtext):
                crossinstallutil.setuplog(0, "Installer finished successfully, moving to step 7")
                step = 7
            else:
                crossinstallutil.setuplog(3, "Installer failed, moving to error step 89")
                step = 89

            nextstep = self.root_obj.findChild(QObject, f"step{step}")
            prevstep = self.root_obj.findChild(QObject, f"step{self.step}")
            if prevstep:
                prevstep.setProperty("visible", False)
            if nextstep:
                nextstep.setProperty("visible", True)
            self.step = step

if __name__ == "__main__":
    crossinstallutil.setuplog(0, "Installer started.")

    willrun = True

    if not is_admin():
        crossinstallutil.setuplog(1, "Not running as admin, relaunching installer with elevation.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        willrun = False
        quit()

    app = QApplication(sys.argv)

    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        k = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\M1PPLauncher")
        winreg.CloseKey(k)
        crossinstallutil.setuplog(1, "M1PP Launcher is already installed.")

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("M1PP Launcher is already installed!")
        msg.setWindowTitle("Error")
        msg.exec_()

        QApplication.instance().quit()
        willrun = False
    except Exception:
        crossinstallutil.setuplog(0, "No existing installation found.")

    if willrun:
        loop = qasync.QEventLoop(app)
        engine = QQmlApplicationEngine()
        window = MainWindow()

        engine.rootContext().setContextProperty("window", window)
        engine.load(resource_path("steps.qml"))

        window.engine = engine
        crossinstallutil.setuplog(0, f"Initial osu! path: {window.osupath}")

        if engine.rootObjects():
            root_obj = engine.rootObjects()[0]
            window.root_obj = root_obj

        with loop:
            loop.run_forever()
