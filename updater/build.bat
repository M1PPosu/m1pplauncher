@echo off
setlocal

set "CURDIR=%~dp0"

pyinstaller --noconfirm --onefile --windowed ^
--name "m1ppupdater" ^
--icon "%CURDIR%icon.ico" ^
--uac-admin ^
--add-data "%CURDIR%gui.qml;." ^
"%CURDIR%main.py"

endlocal
pause