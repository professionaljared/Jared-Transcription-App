[Setup]
AppName=Jared Transcription App
AppVersion=2.0
DefaultDirName={userdesktop}\JTA - Okra
DefaultGroupName=JTA - Okra
OutputDir="C:\users\joeroberts\Documents\MarcyLabWorld\environment\Converter App\dist"
OutputBaseFilename=JTA_Okra_Installer
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64  
DisableProgramGroupPage=yes

[Files]
; Main Executable
Source: "C:\users\joeroberts\Documents\MarcyLabWorld\environment\Converter App\build\exe.win-amd64-3.10\jta_windows.exe"; DestDir: "{app}"; Flags: ignoreversion

; Python DLLs
Source: "C:\users\joeroberts\Documents\MarcyLabWorld\environment\Converter App\build\exe.win-amd64-3.10\python3.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\users\joeroberts\Documents\MarcyLabWorld\environment\Converter App\build\exe.win-amd64-3.10\python310.dll"; DestDir: "{app}"; Flags: ignoreversion

; License File
Source: "C:\users\joeroberts\Documents\MarcyLabWorld\environment\Converter App\build\exe.win-amd64-3.10\frozen_application_license.txt"; DestDir: "{app}"; Flags: ignoreversion

; FFmpeg Folder
Source: "C:\users\joeroberts\Documents\MarcyLabWorld\environment\Converter App\build\exe.win-amd64-3.10\ffmpeg\*"; DestDir: "{app}\ffmpeg"; Flags: ignoreversion recursesubdirs createallsubdirs

; Icons Folder
Source: "C:\users\joeroberts\Documents\MarcyLabWorld\environment\Converter App\build\exe.win-amd64-3.10\icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

; Library Folder - Includes all standard libraries, Python modules, and dependencies
Source: "C:\users\joeroberts\Documents\MarcyLabWorld\environment\Converter App\build\exe.win-amd64-3.10\lib\*"; DestDir: "{app}\lib"; Flags: ignoreversion recursesubdirs createallsubdirs

; Share Folder (tcl and tk)
Source: "C:\users\joeroberts\Documents\MarcyLabWorld\environment\Converter App\build\exe.win-amd64-3.10\share\*"; DestDir: "{app}\share"; Flags: ignoreversion recursesubdirs createallsubdirs

; Explicitly add Python standard libraries to prevent missing essential files like 'encodings'
Source: "C:\users\joeroberts\AppData\Local\Programs\Python\Python310\Lib\*"; DestDir: "{app}\lib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\users\joeroberts\AppData\Local\Programs\Python\Python310\Lib\encodings\*"; DestDir: "{app}\lib\encodings"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\users\joeroberts\AppData\Local\Programs\Python\Python310\Lib\tkinter\*"; DestDir: "{app}\lib\tkinter"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\users\joeroberts\AppData\Local\Programs\Python\Python310\Lib\site-packages\tqdm\*"; DestDir: "{app}\lib\tqdm"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Create Start Menu and Desktop shortcuts
Name: "{group}\JTA - Okra"; Filename: "{app}\jta_windows.exe"; IconFilename: "{app}\icons\jta_logo.ico"
Name: "{commondesktop}\JTA - Okra"; Filename: "{app}\jta_windows.exe"; IconFilename: "{app}\icons\jta_logo.ico"

[Run]
; Run the main executable after installation
Filename: "{app}\jta_windows.exe"; Description: "Launch Jared Transcription App"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Ensure that folders are deleted during uninstallation
Type: filesandordirs; Name: "{app}\lib"
Type: filesandordirs; Name: "{app}\ffmpeg"
Type: filesandordirs; Name: "{app}\icons"
Type: filesandordirs; Name: "{app}\share"