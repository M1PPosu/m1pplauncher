@echo off
setlocal

set "CURDIR=%~dp0"

py -m PyInstaller --noconfirm --onefile --windowed ^
--paths "%CURDIR%.." ^
--hidden-import m1pp_logger ^
--icon "%CURDIR%icon.ico" ^
--name "m1ppinstaller" ^
--uac-admin ^
--add-data "%CURDIR%steps.qml;." ^
--add-data "%CURDIR%..\gui.qml;." ^
--add-data "%CURDIR%..\icon.png;." ^
--add-data "%CURDIR%..\fade.png;." ^
--add-data "%CURDIR%..\unknown.png;." ^
--add-data "%CURDIR%..\slides;slides" ^
"%CURDIR%main.py"

endlocal
pause
