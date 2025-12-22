@echo off
setlocal

set "CURDIR=%~dp0"

pyinstaller --noconfirm --onefile --windowed --icon "%CURDIR%icon.ico" --name "m1pplauncher" ^
--add-data "%CURDIR%fade.png;." ^
--add-data "%CURDIR%gui.qml;." ^
--add-data "%CURDIR%icon.ico;." ^
--add-data "%CURDIR%icon.png;." ^
--add-data "%CURDIR%updater\dist\m1ppupdater.exe;." ^
--add-data "%CURDIR%unknown.png;." ^
"%CURDIR%main.py"

endlocal
pause
