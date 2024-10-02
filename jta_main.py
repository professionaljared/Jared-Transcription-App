import os
import wave
import json
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Import ttk for themed widgets
import threading
import platform  # Import platform to detect the operating system

# Import Vosk modules
try:
    from vosk import Model, KaldiRecognizer
except ImportError:
    # If vosk is not found, inform the user
    messagebox.showerror("Error", "The 'vosk' library is not installed. Please make sure it is bundled correctly with the application.")
    sys.exit(1)

# Function to extract the audio from a video file (using the bundled ffmpeg)
def extract_audio_from_video(video_file_path, output_audio_path):
    if getattr(sys, 'frozen', False):
        ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg", "windows", "ffmpeg.exe" if platform.system() == "Windows" else "macos", "ffmpeg")
    else:
        ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "windows", "ffmpeg.exe" if platform.system() == "Windows" else "macos", "ffmpeg")
    
    if platform.system() != "Windows":
        os.chmod(ffmpeg_path, 0o755)
    
    command = f'"{ffmpeg_path}" -i "{video_file_path}" -ac 1 -ar 16000 -vn "{output_audio_path}"'
    os.system(command)

# Function to transcribe audio using Vosk
def transcribe_audio(audio_file_path):
    # Determine the correct model path
    if getattr(sys, 'frozen', False):
        # If running as a bundled app
        base_path = os.path.dirname(sys.executable)
        model_path = os.path.join(base_path, "model/vosk-model-en-us-0.22")
    else:
        # If running in a regular Python environment
        model_path = os.path.join(os.getcwd(), "model/vosk-model-en-us-0.22")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError("Vosk model directory not found. Please make sure the model is included with the application.")
    
    model = Model(model_path)
    wf = wave.open(audio_file_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError("Audio file must be WAV format mono PCM.")
    
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    transcript = []
    
    total_frames = wf.getnframes()
    processed_frames = 0

    # Function to update the progress bar
    def update_progress():
        progress = (processed_frames / total_frames) * 100
        progress_bar['value'] = progress
        progress_label.config(text=f"Processing: {int(progress)}%")
        root.update_idletasks()

    while True:
        data = wf.readframes(32000)
        if len(data) == 0:
            break
        
        processed_frames += len(data) // wf.getsampwidth()
        root.after(0, update_progress)  # Schedule the GUI update
        
        if rec.AcceptWaveform(data):
            result = rec.Result()
            text = json.loads(result)['text']
            transcript.append(text)
    
    final_transcript = " ".join(transcript)
    return final_transcript

# Function to handle the full transcription process

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # For PyInstaller frozen app
        base_path = sys._MEIPASS
    elif getattr(sys, 'frozen', False):
        # For cx_Freeze frozen app
        base_path = os.path.dirname(sys.executable)
    else:
        # When running in a normal Python environment
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def transcribe_file():
    try:
        select_file_button.config(state=tk.DISABLED)
        progress_bar['value'] = 0
        progress_label.config(text="Starting...")
        
        file_path = filedialog.askopenfilename(title="Select an audio or video file", filetypes=[("Audio/Video Files", "*.wav *.mp4")])
        
        if not file_path:
            select_file_button.config(state=tk.NORMAL)
            return
        
        temp_audio_path = get_resource_path("temp_extracted_audio.wav")

        # Check if temp_extracted_audio.wav exists, and delete it if found
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        if file_path.endswith(".mp4"):
            extract_audio_from_video(file_path, temp_audio_path)
            file_path = temp_audio_path

            # Check if the extraction succeeded
            if not os.path.exists(temp_audio_path):
                raise FileNotFoundError(f"Audio file not found at: {temp_audio_path}")

        # Transcribe the audio file
        transcript = transcribe_audio(file_path)
        
        # Ask where to save the transcript file
        save_transcript_path = filedialog.asksaveasfilename(title="Save Transcript as", defaultextension=".txt")
        with open(save_transcript_path, "w") as f:
            f.write(transcript)
        
        # Delete the temporary audio file if it was created
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        messagebox.showinfo("Success", "Transcription completed successfully!")
        progress_label.config(text="Transcription completed!")
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        progress_label.config(text="An error occurred.")
    
    finally:
        select_file_button.config(state=tk.NORMAL)

# Function to start the transcription process in a separate thread

def start_transcription():
    thread = threading.Thread(target=transcribe_file)
    thread.start()

# Tkinter GUI setup
root = tk.Tk()
root.title("JTA - Turnip (1.1)")
root.geometry("600x400")

# Create a ttk style and set a theme
style = ttk.Style()
style.theme_use("clam")

# Configure a custom style for ttk labels
style.configure("Custom.TLabel", background="#3aae48", foreground="black", font=("Helvetica", 12), padding=10)

# Create a frame to organize widgets
main_frame = ttk.Frame(root)
main_frame.grid(row=0, column=0, sticky="nsew")

# Add a ttk label
welcome_label = ttk.Label(main_frame, text="Welcome to JTA - Turnip (1.1)", style="Custom.TLabel")
welcome_label.grid(row=0, column=0, padx=10, pady=10)

# Add a ttk button for selecting a file and transcribing
select_file_button = ttk.Button(main_frame, text="Select File and Transcribe", command=start_transcription)
select_file_button.grid(row=1, column=0, padx=10, pady=20)

# Add a progress bar
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=500, mode="determinate")
progress_bar.grid(row=2, column=0, padx=10, pady=10)

# Add a label to show progress percentage
progress_label = ttk.Label(main_frame, text="Progress: 0%", style="Custom.TLabel")
progress_label.grid(row=3, column=0, padx=10, pady=5)

# Ensure the window expands correctly
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Start the Tkinter loop
root.mainloop()
