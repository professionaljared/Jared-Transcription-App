[Setup]
AppName=JTA
AppVersion=1.0
DefaultDirName={autopf}\JTA
DefaultGroupName=JTA
OutputDir=output
OutputBaseFilename=JTA_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\jta_main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\download_model.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ffmpeg\*"; DestDir: "{app}\ffmpeg"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\JTA"; Filename: "{app}\jta_main.exe"
Name: "{group}\Uninstall JTA"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\download_model.exe"; Description: "Download Vosk Model"; Flags: nowait postinstall skipifsilent
