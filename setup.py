import os
import platform
from cx_Freeze import setup, Executable

# Determine the paths for included resources like ffmpeg and its libraries
if platform.system() == "Windows":
    ffmpeg_bin = os.path.join("ffmpeg", "windows", "ffmpeg.exe")
else:
    ffmpeg_bin = os.path.join("ffmpeg", "macos", "ffmpeg")
    # ffmpeg_lib = os.path.join("ffmpeg", "macos", "lib")

# Add the model folder to be included
model_folder = "model"

# Build executable options
build_exe_options = {
    "packages": ["os", "wave", "json", "subprocess", "tkinter", "threading", "tempfile", "platform"],
    "include_files": [
        (ffmpeg_bin, "ffmpeg/macos/ffmpeg"),  # Include the ffmpeg binary
        # (ffmpeg_lib, "ffmpeg/macos/lib"),  # Include the FFmpeg libraries for macOS
        (model_folder, "model")  # Include the Vosk model directory
    ],
    "optimize": 2
}

# Application setup
setup(
    name="JTA - Turnip",
    version="1.1",
    description="Jared Transcription App",
    options={"build_exe": build_exe_options},
    executables=[Executable("jta_main.py", target_name="jta_main", base="Console" if platform.system() != "Windows" else None)]
)
