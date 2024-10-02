import sys
from cx_Freeze import setup, Executable
import os

# Build options
build_exe_options = {
    "packages": ["os", "tkinter", "vosk"],  # Include necessary packages
    "excludes": [],  # Exclude any unnecessary packages if needed
    "include_files": [
        ("/Users/joeroberts/Documents/MarcyLabWorld/environment/Converter App/ffmpeg", "ffmpeg"),  # Path to the ffmpeg folder
        ("/Users/joeroberts/Documents/MarcyLabWorld/environment/Converter App/model", "model"),    # Path to the model folder
        ("/Users/joeroberts/Documents/MarcyLabWorld/environment/Converter App/venv310/lib/python3.10/site-packages/vosk", "vosk"),  # Path to the vosk library
    ],
}

# Define the build directory to be 'output'
build_dir = "output"

# Target executable options
executables = [
    Executable(
        "jta_main.py"  # Path to your main Python file
    )
]

# Setup configuration
setup(
    name="JTA",
    version="1.1",
    description="Jared Transcription App",
    options={"build_exe": build_exe_options},
    executables=executables
)

# Moving the build result to the desired directory
if os.path.exists(build_dir):
    print(f"Build will be placed in '{build_dir}'")
else:
    os.makedirs(build_dir)
