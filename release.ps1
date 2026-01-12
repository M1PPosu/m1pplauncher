[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$Version,

  [string]$PyInstallerTag = "v6.17.0",

  [string]$PythonLauncher = "py"  
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

Write-Host "== M1PP Release Build ==" -ForegroundColor Cyan
Write-Host "RepoRoot: $RepoRoot"
Write-Host "Version : $Version"
Write-Host ""

function Import-VSBuildEnv {
  param(
    [string]$Arch = "x64",
    [string]$HostArch = "x64"
  )

  $vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
  if (!(Test-Path $vswhere)) {
    throw "vswhere.exe not found at: $vswhere. Install Visual Studio Installer / VS Build Tools."
  }

  $vsPath = & $vswhere -latest -products * `
    -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
    -property installationPath

  if (-not $vsPath) {
    throw "No VS instance with MSVC x64 tools found. Install 'Desktop development with C++' or VS Build Tools (MSVC x64)."
  }

  $vsDevCmd = Join-Path $vsPath "Common7\Tools\VsDevCmd.bat"
  if (!(Test-Path $vsDevCmd)) {
    throw "VsDevCmd.bat not found at: $vsDevCmd"
  }

  $cmd = "`"$vsDevCmd`" -no_logo -arch=$Arch -host_arch=$HostArch && set"
  cmd.exe /c $cmd | ForEach-Object {
    if ($_ -match "^(.*?)=(.*)$") {
      $name = $matches[1]
      $value = $matches[2]
      Set-Item -Path ("Env:{0}" -f $name) -Value $value
    }
  }
}

function Find-FirstExisting {
  param(
    [Parameter(Mandatory=$true)]
    [string[]]$Candidates,
    [string]$Label = "entry"
  )
  foreach ($c in $Candidates) {
    $p = Join-Path $RepoRoot $c
    if (Test-Path $p) { return $p }
  }
  $msg = "Could not find $Label. Tried:`n" + ($Candidates | ForEach-Object { "  - $_" } | Out-String)
  throw $msg
}

function Ensure-Dir([string]$Path) {
  New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Remove-IfExists([string]$Path) {
  if (Test-Path $Path) { Remove-Item -Recurse -Force $Path }
}

Import-VSBuildEnv -Arch x64 -HostArch x64
if (-not (Get-Command cl.exe -ErrorAction SilentlyContinue)) {
  throw "MSVC not available (cl.exe missing) even after Import-VSBuildEnv."
}
Write-Host "MSVC OK: $((Get-Command cl.exe).Source)" -ForegroundColor Green
Write-Host ""

$VenvDir = Join-Path $RepoRoot ".venv"
$VenvPy  = Join-Path $VenvDir "Scripts\python.exe"
$VenvPip = Join-Path $VenvDir "Scripts\pip.exe"
$VenvPyi = Join-Path $VenvDir "Scripts\pyinstaller.exe"

Write-Host "Creating venv at $VenvDir ..."
if (!(Test-Path $VenvPy)) {
  & $PythonLauncher -3.12 -m venv $VenvDir
}
& $VenvPy -m pip install -U pip setuptools wheel | Out-Host

$Req = Join-Path $RepoRoot "requirements.txt"
Write-Host "Installing build/runtime dependencies into venv ..."
if (Test-Path $Req) {
  & $VenvPy -m pip install -r $Req | Out-Host
} else {
  & $VenvPy -m pip install `
    PySide6 qasync psutil aiohttp aiofiles requests winshell pyautogui | Out-Host
}

$ToolsDir = Join-Path $RepoRoot ".tools"
$PyISrc   = Join-Path $ToolsDir "pyinstaller-src"
Ensure-Dir $ToolsDir

if (!(Test-Path $PyISrc)) {
  Write-Host "Cloning PyInstaller source..."
  git clone https://github.com/pyinstaller/pyinstaller.git $PyISrc | Out-Host
}

Push-Location $PyISrc
git fetch --tags --force | Out-Host
git checkout $PyInstallerTag | Out-Host

Write-Host "Building PyInstaller bootloader (MSVC)..." -ForegroundColor Cyan
Push-Location (Join-Path $PyISrc "bootloader")
& $VenvPy .\waf all | Out-Host
Pop-Location

Write-Host "Installing PyInstaller from source into venv..." -ForegroundColor Cyan
& $VenvPy -m pip install -U . | Out-Host
if (!(Test-Path $VenvPyi)) {
  throw "pyinstaller.exe not found in venv after install. Expected: $VenvPyi"
}
Write-Host "PyInstaller OK: $(& $VenvPyi --version)" -ForegroundColor Green
Pop-Location
Write-Host ""

$LauncherEntry  = Find-FirstExisting -Label "launcher entry" -Candidates @(
  "main.py",
  "launcher.py",
  "app.py"
)

$UpdaterEntry   = Find-FirstExisting -Label "updater entry" -Candidates @(
  "m1ppupdater.py",
  "updater.py",
  "updater\main.py",
  "updater_main.py"
)

$InstallerEntry = Find-FirstExisting -Label "installer entry" -Candidates @(
  "installer.py",
  "install.py",
  "setup.py",
  "installer\main.py",
  "installer_main.py"
)

Write-Host "Launcher : $LauncherEntry"
Write-Host "Updater  : $UpdaterEntry"
Write-Host "Installer: $InstallerEntry"
Write-Host ""

$Common = @("--noconfirm","--clean","-w")

$DataArgs = @()
$GuiQml = Join-Path $RepoRoot "gui.qml"
$IconPng = Join-Path $RepoRoot "icon.png"
$BuiltinMods = Join-Path $RepoRoot "builtinmods"

if (Test-Path $GuiQml)     { $DataArgs += @("--add-data", "$GuiQml;.") }
if (Test-Path $IconPng)    { $DataArgs += @("--add-data", "$IconPng;.") }
if (Test-Path $BuiltinMods){ $DataArgs += @("--add-data", "$BuiltinMods;builtinmods") }

$BuildRoot = Join-Path $RepoRoot "build"
$OutDir    = Join-Path $RepoRoot ("release\" + $Version)

Remove-IfExists $BuildRoot
Ensure-Dir $BuildRoot
Remove-IfExists $OutDir
Ensure-Dir $OutDir

$DistUpdater   = Join-Path $BuildRoot "dist-updater"
$WorkUpdater   = Join-Path $BuildRoot "work-updater"
$DistLauncher  = Join-Path $BuildRoot "dist-launcher"
$WorkLauncher  = Join-Path $BuildRoot "work-launcher"
$DistInstaller = Join-Path $BuildRoot "dist-installer"
$WorkInstaller = Join-Path $BuildRoot "work-installer"

Write-Host "Building updater..." -ForegroundColor Cyan
& $VenvPyi @Common -F `
  -n "m1ppupdater" `
  --distpath $DistUpdater `
  --workpath $WorkUpdater `
  @DataArgs `
  $UpdaterEntry | Out-Host

$UpdaterExe = Join-Path $DistUpdater "m1ppupdater.exe"
if (!(Test-Path $UpdaterExe)) { throw "Updater exe missing: $UpdaterExe" }

Write-Host "Building launcher..." -ForegroundColor Cyan
$LauncherExtras = @("--add-binary", "$UpdaterExe;.")
& $VenvPyi @Common -F `
  -n "m1pplauncher" `
  --distpath $DistLauncher `
  --workpath $WorkLauncher `
  @DataArgs `
  @LauncherExtras `
  $LauncherEntry | Out-Host

$LauncherExe = Join-Path $DistLauncher "m1pplauncher.exe"
if (!(Test-Path $LauncherExe)) { throw "Launcher exe missing: $LauncherExe" }

Write-Host "Building installer..." -ForegroundColor Cyan
$InstallerExtras = @(
  "--uac-admin",
  "--add-binary", "$LauncherExe;.",
  "--add-binary", "$UpdaterExe;."
)

& $VenvPyi @Common -F `
  -n "M1PPInstaller" `
  --distpath $DistInstaller `
  --workpath $WorkInstaller `
  @DataArgs `
  @InstallerExtras `
  $InstallerEntry | Out-Host

$InstallerExe = Join-Path $DistInstaller "M1PPInstaller.exe"
if (!(Test-Path $InstallerExe)) { throw "Installer exe missing: $InstallerExe" }

Write-Host "Collecting release artifacts..." -ForegroundColor Cyan
Copy-Item $InstallerExe (Join-Path $OutDir ("M1PPInstaller-$Version.exe")) -Force
Copy-Item $LauncherExe  (Join-Path $OutDir ("m1pplauncher-$Version.exe"))  -Force
Copy-Item $UpdaterExe   (Join-Path $OutDir ("m1ppupdater-$Version.exe"))   -Force

Write-Host ""
Write-Host "DONE." -ForegroundColor Green
Write-Host "Release folder: $OutDir"
Write-Host "  - M1PPInstaller-$Version.exe"
Write-Host "  - m1pplauncher-$Version.exe"
Write-Host "  - m1ppupdater-$Version.exe"
