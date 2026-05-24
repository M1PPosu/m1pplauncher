@echo off
setlocal

for %%I in ("%~dp0.") do set "ROOT=%%~fI"
set "SCRIPT=%ROOT%\packaging\windows\m1pplauncher.iss"
set "ISCC_EXE="

call "%ROOT%\build.bat"
if errorlevel 1 exit /b 1

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not defined ISCC_EXE if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 6\ISCC.exe"
if not defined ISCC_EXE if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not defined ISCC_EXE (
  echo Inno Setup compiler not found. Install Inno Setup 6 and ensure ISCC.exe is available.
  exit /b 1
)

"%ISCC_EXE%" "%SCRIPT%"
if errorlevel 1 exit /b 1

if not exist "%ROOT%\dist\installer\M1PPLauncherSetup.exe" (
  echo Installer build did not produce dist\installer\M1PPLauncherSetup.exe
  exit /b 1
)

echo Built installer: %ROOT%\dist\installer\M1PPLauncherSetup.exe
endlocal
