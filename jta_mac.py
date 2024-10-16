import os
import wave
import json
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
from vosk import Model, KaldiRecognizer
from jta_ui import initialize_ui # UI Import

def get_documents_folder():
    return os.path.join(os.environ['HOME'], 'Documents')

def get_temp_audio_path():
    documents_folder = get_documents_folder()
    temp_audio_folder = os.path.join(documents_folder, "JTA - Jared Transcription App")
    os.makedirs(temp_audio_folder, exist_ok=True)
    return os.path.join(temp_audio_folder, "temp_extracted_audio.wav")

# Get the ffmpeg path

def get_ffmpeg_path():
    """
    Determine the correct path for the ffmpeg binary based on whether the app is frozen (cx_Freeze).
    """
    # Check if the application is frozen (packaged by cx_Freeze)
    if getattr(sys, 'frozen', False):
        # If frozen, adjust the ffmpeg path based on the app's executable location
        base_path = os.path.dirname(sys.executable)
        ffmpeg_path = os.path.join(base_path, "ffmpeg", "macos", "ffmpeg")
    else:
        # If not frozen, use the current working directory (development environment)
        ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "macos", "ffmpeg")

    return ffmpeg_path

# Extract audio from video using ffmpeg

def extract_audio_from_video(video_file_path, output_audio_path):
    # Use the get_ffmpeg_path function to determine the correct path for ffmpeg
    ffmpeg_path = get_ffmpeg_path()
    progress_label.config(text="Extracting Audio...")

    # Ensure ffmpeg is executable
    os.chmod(ffmpeg_path, 0o755)

    # Use list of command components to avoid shell interpretation issues
    command = [
        ffmpeg_path,
        '-i', video_file_path,
        '-ac', '1',
        '-ar', '16000',
        '-vn',
        '-preset', 'ultrafast',
        output_audio_path
    ]

    try:
        subprocess.run(command, check=True)
        print("Audio extraction completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to extract audio. Command: {command}")
        raise e

# Transcribe audio using Vosk model
def transcribe_audio(audio_file_path):
    # Determine the correct model path
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  # In bundled app
    else:
        base_path = os.path.dirname(__file__)  # In development
    
    model_path = os.path.join(base_path, "model/vosk-model-en-us-0.22")
    
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
        data = wf.readframes(64000)
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

# File selection and transcription function
def transcribe_file():
    try:
        select_file_button.config(state=tk.DISABLED)
        progress_bar['value'] = 0
        
        file_path = filedialog.askopenfilename(title="Select an audio or video file", filetypes=[("Audio/Video Files", "*.wav *.mp4")])
        progress_label.config(text="Selecting File...")
        if not file_path:
            select_file_button.config(state=tk.NORMAL)
            progress_label.config(text="Awaiting File...")
            return
        
        # Get the base path for temp files
        documents_folder = os.path.join(os.path.expanduser('~'), 'Documents')
        
        temp_audio_folder = os.path.join(documents_folder, "JTA - Jared Transcription App")
        if not os.path.exists(temp_audio_folder):
            os.makedirs(temp_audio_folder)
        
        temp_audio_path = os.path.join(temp_audio_folder, "temp_extracted_audio.wav")

        # Check if temp_extracted_audio.wav exists, and delete it if found
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        if file_path.endswith(".mp4"):
            # Extract audio in a separate thread to improve responsiveness
            extraction_thread = threading.Thread(target=extract_audio_from_video, args=(file_path, temp_audio_path))
            extraction_thread.start()
            progress_label.config(text="Starting...")
            extraction_thread.join()
            file_path = temp_audio_path

        # Transcribe the audio file in a separate thread
        transcription_thread = threading.Thread(target=transcribe_and_save, args=(file_path,))
        transcription_thread.start()
        transcription_thread.join()
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        progress_label.config(text="An error occurred.")
    
    finally:
        select_file_button.config(state=tk.NORMAL)

# Function to handle transcription and saving
def transcribe_and_save(file_path):
    # Transcribe the audio file
    transcript = transcribe_audio(file_path)
    
    # Ask where to save the transcript file
    save_transcript_path = filedialog.asksaveasfilename(initialfile="Untitled", title="Save Transcript as", defaultextension=".txt")
    if save_transcript_path:
        with open(save_transcript_path, "w") as f:
            f.write(transcript)
    
    # Delete the temporary audio file if it was created
    temp_audio_path = get_temp_audio_path()
    if temp_audio_path and os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)

    messagebox.showinfo("Success", "Transcription completed successfully!")
    progress_label.config(text="Transcription completed!")

def start_transcription():
    # Start the transcription process in a separate thread to avoid blocking the GUI
    thread = threading.Thread(target=transcribe_file)
    thread.start()
# Tkinter GUI setup

def open_settings_window():
    # Create a new settings window
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x200")
    
    # Add settings options (you can add more settings here)
    label = ttk.Label(settings_window, text="Settings Page", font=("Helvetica", 14))
    label.pack(pady=20)

    close_button = ttk.Button(settings_window, text="Close", command=settings_window.destroy)
    close_button.pack(pady=10)


# Version attributes

# Initialize the UI
root, select_file_button, progress_bar, progress_label = initialize_ui(
    transcribe_file_command=lambda: threading.Thread(target=transcribe_file).start(),
    settings_command=open_settings_window
)

# Start the Tkinter loop
if __name__ == "__main__":
    root.mainloop()