@echo off
setlocal

set "PYTHON_CMD=py -3.13"
for %%I in ("%~dp0.") do set "ROOT=%%~fI"
set "UPDATER_WORK=%ROOT%\build\updater"
set "UPDATER_DIST=%ROOT%\dist\updater"
set "LAUNCHER_WORK=%ROOT%\build\launcher"
set "LAUNCHER_DIST=%ROOT%\dist\launcher"
set "UPDATER_EXE=%UPDATER_DIST%\m1ppupdater.exe"

%PYTHON_CMD% -c "from PySide6 import QtCore, QtGui, QtWidgets, QtQml"
if errorlevel 1 exit /b 1

if exist "%UPDATER_WORK%" rmdir /s /q "%UPDATER_WORK%"
if exist "%UPDATER_DIST%" rmdir /s /q "%UPDATER_DIST%"
if exist "%LAUNCHER_WORK%" rmdir /s /q "%LAUNCHER_WORK%"
if exist "%LAUNCHER_DIST%" rmdir /s /q "%LAUNCHER_DIST%"

%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --windowed --name "m1ppupdater" --icon "%ROOT%\updater\icon.ico" --uac-admin --paths "%ROOT%" --specpath "%UPDATER_WORK%" --workpath "%UPDATER_WORK%" --distpath "%UPDATER_DIST%" --hidden-import PySide6 --hidden-import PySide6.QtCore --hidden-import PySide6.QtWidgets --hidden-import PySide6.QtQml --add-data "%ROOT%\updater\gui.qml;." "%ROOT%\updater\main.py"
if errorlevel 1 exit /b 1

%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --windowed --name "m1pplauncher" --icon "%ROOT%\icon.ico" --specpath "%LAUNCHER_WORK%" --workpath "%LAUNCHER_WORK%" --distpath "%LAUNCHER_DIST%" --hidden-import PySide6 --hidden-import PySide6.QtCore --hidden-import PySide6.QtGui --hidden-import PySide6.QtWidgets --hidden-import PySide6.QtQml --add-data "%ROOT%\gui.qml;." --add-data "%ROOT%\fade.png;." --add-data "%ROOT%\slides;slides" --add-data "%ROOT%\font;font" --add-data "%ROOT%\icon.png;." --add-data "%ROOT%\builtinmods;builtinmods" --add-binary "%UPDATER_EXE%;." "%ROOT%\main.py"
if errorlevel 1 exit /b 1

echo Built launcher: %LAUNCHER_DIST%\m1pplauncher.exe
endlocal
