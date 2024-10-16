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
import concurrent.futures
from vosk import Model, KaldiRecognizer

# Attributes for the version name and number
version_name = "Ginger"
version_number = "1.3"

def get_documents_folder():
    return os.path.join(os.environ['USERPROFILE'], 'Documents')

def get_temp_audio_path():
    documents_folder = get_documents_folder()
    temp_audio_folder = os.path.join(documents_folder, "JTA - Jared Transcription App")
    os.makedirs(temp_audio_folder, exist_ok=True)
    return os.path.join(temp_audio_folder, "temp_extracted_audio.wav")

# Get the ffmpeg path
def get_ffmpeg_path():
    # Check if the application is frozen (packaged by cx_Freeze)
    if getattr(sys, 'frozen', False):
        # If frozen, adjust the ffmpeg path based on the app's executable location
        base_path = os.path.dirname(sys.executable)
        ffmpeg_path = os.path.join(base_path, "ffmpeg", "windows", "ffmpeg.exe")
    else:
        # If not frozen, use the current working directory (development environment)
        ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "windows", "ffmpeg.exe")

    return ffmpeg_path

# Extract audio from video using ffmpeg
def extract_audio_from_video(video_file_path, output_audio_path):
    # Use the get_ffmpeg_path function to determine the correct path for ffmpeg
    ffmpeg_path = get_ffmpeg_path()
    progress_label.config(text="Extracting Audio...")

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

# Transcribe a chunk of audio using Vosk model
def transcribe_audio_chunk(model, chunk_data, framerate, chunk_index):
    rec = KaldiRecognizer(model, framerate)
    rec.SetWords(True)
    transcript = []

    if rec.AcceptWaveform(chunk_data):
        result = rec.Result()
        text = json.loads(result)['text']
        transcript.append((chunk_index, text))
    else:
        partial_result = rec.PartialResult()
        text = json.loads(partial_result).get('partial', '')
        if text:
            transcript.append((chunk_index, text))

    return transcript

# Split audio into chunks and transcribe using multiple threads
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
    
    total_frames = wf.getnframes()
    chunk_size = 16000 * 60  # 60 seconds per chunk
    chunks = []

    # Read the audio file in chunks
    chunk_index = 0
    while True:
        data = wf.readframes(chunk_size)
        if len(data) == 0:
            break
        chunks.append((chunk_index, data))
        chunk_index += 1
    
    # Transcribe chunks using ThreadPoolExecutor
    transcript = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(transcribe_audio_chunk, model, chunk[1], wf.getframerate(), chunk[0]) for chunk in chunks]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            transcript.extend(future.result())
            progress = ((i + 1) / len(futures)) * 100
            progress_bar['value'] = progress
            progress_label.config(text=f"Processing: {int(progress)}%")
            root.update_idletasks()
    
    # Sort transcript by chunk index to ensure correct order
    transcript.sort(key=lambda x: x[0])
    final_transcript = " ".join([text for _, text in transcript])
    return final_transcript

# File selection and transcription function
def transcribe_file():
    try:
        select_file_button.config(state=tk.DISABLED)
        progress_bar['value'] = 0
        progress_label.config(text="Selecting File...")
        
        file_path = filedialog.askopenfilename(title="Select an audio or video file", filetypes=[("Audio/Video Files", "*.wav *.mp4")])

        if not file_path:
            select_file_button.config(state=tk.NORMAL)
            progress_label.config(text="Awaiting File...")
            return
        
        # Get the base path for temp files
        documents_folder = os.path.join(os.getenv('USERPROFILE'), 'Documents')
        
        temp_audio_folder = os.path.join(documents_folder, "JTA - Jared Transcription App")
        if not os.path.exists(temp_audio_folder):
            os.makedirs(temp_audio_folder)
        
        temp_audio_path = os.path.join(temp_audio_folder, "temp_extracted_audio.wav")

        # Check if temp_extracted_audio.wav exists, and delete it if found
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        if file_path.endswith(".mp4"):
            # Extract audio
            extract_audio_from_video(file_path, temp_audio_path)
            file_path = temp_audio_path

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
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        progress_label.config(text="An error occurred.")
    
    finally:
        select_file_button.config(state=tk.NORMAL)

def start_transcription():
    # Start the transcription process in a separate thread to avoid blocking the GUI
    thread = threading.Thread(target=transcribe_file)
    thread.start()

#  Tkinter GUI setup

root = tk.Tk()
root.title(f"JTA - {version_name} ({version_number})")
root.geometry("600x400")

# Create a ttk style and set a theme
style = ttk.Style()
style.theme_use("clam")

# Configure a custom style for ttk labels
style.configure("Custom.TLabel", background="#E9A365", foreground="black", font=("Helvetica", 12), padding=10)

# Create a frame to organize widgets
main_frame = ttk.Frame(root)
main_frame.grid(row=0, column=0, sticky="nsew")

# Add a ttk label
welcome_label = ttk.Label(main_frame, text=f"Welcome to JTA - {version_name} ({version_number})", style="Custom.TLabel")
welcome_label.grid(row=0, column=0, padx=10, pady=10)

# Add a ttk button for selecting a file and transcribing
select_file_button = ttk.Button(main_frame, text="Select File and Transcribe", command=start_transcription)
select_file_button.grid(row=1, column=0, padx=10, pady=20)

# Add a progress bar
progress_bar = ttk.Progressbar(main_frame,orient="horizontal", length=500, mode="determinate")
progress_bar.grid(row=2, column=0, padx=10, pady=10)

# Add a label to show progress percentage
progress_label = ttk.Label(main_frame, text="Awaiting File...", style="Custom.TLabel")
progress_label.grid(row=3, column=0, padx=10, pady=5)
# Ensure the window expands correctly
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

if __name__ == "__main__":
    # Start the Tkinter loop
    root.mainloop()
