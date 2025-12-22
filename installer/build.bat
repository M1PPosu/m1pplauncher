@echo off
setlocal

set "CURDIR=%~dp0"

pyinstaller --noconfirm --onefile --windowed ^
--icon "%CURDIR%icon.ico" ^
--name "m1ppinstaller" ^
--uac-admin ^
--add-data "%CURDIR%steps.qml;." ^
"%CURDIR%main.py"

endlocal
pause