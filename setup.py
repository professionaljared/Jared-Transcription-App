import os
import platform
from jta_ui import version_name, version_number
from cx_Freeze import setup, Executable

# Dependencies 
extra_files = []

# Paths for different platforms
if platform.system() == "Windows":
    ffmpeg_bin = os.path.join("ffmpeg", "windows")  # Include the entire Windows FFmpeg folder    
    app_platform = "windows"
    # Torch inclusion (Win)
    torch_lib_path = os.path.join("C:\\users\\joeroberts\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages\\torch\\lib")
    if os.path.exists(torch_lib_path):
        for file_name in os.listdir(torch_lib_path):
            if file_name.endswith(".dll"):
                full_file_path = os.path.join(torch_lib_path, file_name)
                extra_files.append((full_file_path, os.path.join("lib", "torch", "lib", file_name)))
else:
    ffmpeg_bin = os.path.join("ffmpeg", "macos", "ffmpeg")
    app_platform = "mac"
    # Torch inclusion (MacOS)
    torch_lib_path = os.path.join("venv310", "lib", "python3.10", "site-packages", "torch", "lib")
    if os.path.exists(torch_lib_path):
        for file_name in os.listdir(torch_lib_path):
            if file_name.endswith(".dylib"):
                full_file_path = os.path.join(torch_lib_path, file_name)
                extra_files.append((full_file_path, os.path.join("lib", "torch", "lib", file_name)))

icon_folder = "icons"

# Set base based on the platform
base = None
if platform.system() == "Windows":
    base = "Win32GUI"


# Build options for macOS and Windows
build_exe_options = {
    "packages": ["os", "sys", "subprocess", "ssl", "whisper", "threading", "tqdm", "tkinter", "torch", "PIL", "customtkinter"],
    "include_files": [
        (ffmpeg_bin, "ffmpeg/windows/" if platform.system() == "Windows" else "ffmpeg/macos/ffmpeg"),
        (icon_folder, "icons")
    ] + extra_files,  # Include extra shared libraries for both platforms
    "optimize": 2
}

# Setup
setup(
    name=f"JTA - {version_name}",
    version=f"{version_number}",
    description="Jared Transcription App",
    options={"build_exe": build_exe_options},
    executables=[Executable(f"jta_{app_platform}.py", base=base, target_name=f"jta_{app_platform}.exe" if platform.system() == "Windows" else f"jta_{app_platform}")]
)
