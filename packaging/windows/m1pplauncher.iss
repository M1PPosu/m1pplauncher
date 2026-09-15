#define AppName "M1PP Launcher"
#define AppVersion "v4b"
#define AppPublisher "M1PPosu"
#define AppExeName "m1pplauncher.exe"
#define AppId "M1PPLauncher"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\M1PPLauncher
DefaultGroupName={#AppName}
DisableDirPage=no
DisableProgramGroupPage=yes
OutputDir=..\..\dist\installer
OutputBaseFilename=M1PPLauncherSetup
SetupIconFile=..\..\icon.ico
LicenseFile=..\..\LICENSE
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\..\dist\launcher\m1pplauncher.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{userprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[UninstallDelete]
Type: files; Name: "{app}\launchersettings.json"
Type: files; Name: "{app}\installdata.json"
Type: filesandordirs; Name: "{app}\cache"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\mods"
Type: filesandordirs; Name: "{app}\tools"
Type: filesandordirs; Name: "{app}"

[Code]
var
  PreviousInstallDir: string;
  OsuPage: TInputDirWizardPage;

function NormalizeDir(Value: string): string;
begin
  Result := RemoveBackslashUnlessRoot(ExpandConstant(Value));
end;

function JsonString(Value: string): string;
begin
  Result := NormalizeDir(Value);
  StringChangeEx(Result, '\', '\\', True);
  StringChangeEx(Result, '"', '\"', True);
  Result := '"' + Result + '"';
end;

function IsValidOsuStableDir(Value: string): Boolean;
var
  Dir: string;
begin
  Dir := NormalizeDir(Value);
  Result :=
    (Dir <> '') and
    FileExists(Dir + '\osu!.exe') and
    FileExists(Dir + '\osu!auth.dll');
end;

function DefaultOsuStableDir(): string;
var
  Candidate: string;
begin
  Candidate := ExpandConstant('{localappdata}\osu!');
  if IsValidOsuStableDir(Candidate) then
    Result := Candidate
  else
    Result := '';
end;

function InitializeSetup(): Boolean;
begin
  PreviousInstallDir := '';
  RegQueryStringValue(
    HKCU,
    'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppId}_is1',
    'InstallLocation',
    PreviousInstallDir
  );
  Result := True;
end;

procedure InitializeWizard();
begin
  OsuPage := CreateInputDirPage(
    wpSelectDir,
    'Select osu!stable Folder',
    'Choose your existing osu!stable installation folder.',
    'Select the folder that contains osu!.exe and osu!auth.dll.',
    False,
    ''
  );

  OsuPage.Add('osu!stable folder:');
  OsuPage.Values[0] := DefaultOsuStableDir();
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = OsuPage.ID then begin
    if not IsValidOsuStableDir(OsuPage.Values[0]) then begin
      MsgBox(
        'Please select a valid osu!stable folder containing osu!.exe and osu!auth.dll.',
        mbError,
        MB_OK
      );
      Result := False;
    end;
  end;
end;

procedure WriteInstallData();
var
  Path: string;
  Lines: TArrayOfString;
begin
  ForceDirectories(ExpandConstant('{app}\mods'));

  Path := ExpandConstant('{app}\installdata.json');

  SetArrayLength(Lines, 4);
  Lines[0] := '{';
  Lines[1] := '  "m1pppath": ' + JsonString(ExpandConstant('{app}')) + ',';
  Lines[2] := '  "osupath": ' + JsonString(OsuPage.Values[0]);
  Lines[3] := '}';

  SaveStringsToUTF8File(Path, Lines, False);
end;

procedure RemoveOldInstallDir(OldDir: string);
var
  CleanOldDir: string;
begin
  CleanOldDir := NormalizeDir(OldDir);
  if CleanOldDir = '' then
    Exit;

  if CompareText(CleanOldDir, NormalizeDir('{app}')) = 0 then
    Exit;

  if not DirExists(CleanOldDir) then 
    Exit;

  if not FileExists(CleanOldDir + '\{#AppExeName}') and
     not FileExists(CleanOldDir + '\unins000.exe') then
    Exit;

  DeleteFile(CleanOldDir + '\{#AppExeName}');
  DeleteFile(CleanOldDir + '\unins000.exe');
  DeleteFile(CleanOldDir + '\unins000.dat');
  DeleteFile(CleanOldDir + '\launchersettings.json');
  DeleteFile(CleanOldDir + '\installdata.json');
  DelTree(CleanOldDir + '\cache', True, True, True);
  DelTree(CleanOldDir + '\logs', True, True, True);
  DelTree(CleanOldDir + '\mods', True, True, True);
  DelTree(CleanOldDir + '\tools', True, True, True);
  RemoveDir(CleanOldDir);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    WriteInstallData();
    RemoveOldInstallDir(PreviousInstallDir);
  end;
end;
