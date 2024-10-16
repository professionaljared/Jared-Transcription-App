import os
import platform
from jta_mac import version_name, version_number
from cx_Freeze import setup, Executable

# Paths for different platforms
if platform.system() == "Windows":
    ffmpeg_bin = os.path.join("ffmpeg", "windows")  # Include the entire Windows FFmpeg folder    
    vosk_lib = os.path.join("C:\\users\\joeroberts\\AppData\\Local\\Programs\\Python\\Python310\\lib\\site-packages\\vosk")
    app_platform = "windows"
else:
    ffmpeg_bin = os.path.join("ffmpeg", "macos", "ffmpeg")
    vosk_lib = os.path.join("/Users/joeroberts/Documents/MarcyLabWorld/environment/Converter App/venv310/lib/python3.10/site-packages/vosk")
    app_platform = "mac"

# Add the model folder (common for both platforms)
model_folder = "model"

# Set base based on the platform
base = None
if platform.system() == "Windows":
    base = "Win32GUI"

# Build options for macOS and Windows
build_exe_options = {
    "packages": ["os", "wave", "json", "subprocess", "tkinter", "threading", "tempfile", "platform"],
    "include_files": [
        (ffmpeg_bin, "ffmpeg/windows/" if platform.system() == "Windows" else "ffmpeg/macos/ffmpeg"),        
        (vosk_lib, "vosk"),  # Include Vosk library based on the platform
        (model_folder, "model")
    ],
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
