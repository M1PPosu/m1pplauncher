@echo off
setlocal

set "CURDIR=%~dp0"
set "ROOT=%CURDIR%.."

py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --paths "%ROOT%" ^
  --hidden-import m1pp_logger ^
  --icon "%CURDIR%icon.ico" ^
  --name "m1ppinstaller" ^
  --uac-admin ^
  --add-data "%CURDIR%steps.qml;." ^
  --add-data "%ROOT%\gui.qml;." ^
  --add-data "%ROOT%\icon.png;." ^
  --add-data "%ROOT%\fade.png;." ^
  --add-data "%ROOT%\unknown.png;." ^
  --add-data "%ROOT%\slides;slides" ^
  --add-data "%ROOT%\font;font" ^
  "%CURDIR%main.py"

endlocal
pause
