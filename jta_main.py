import os
import wave
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from vosk import Model, KaldiRecognizer
import threading
import platform

MODEL_PATH = "model"  # Path where the model will be downloaded

# Function to extract audio from video using bundled ffmpeg
def extract_audio_from_video(video_file_path, output_audio_path):
    if platform.system() == "Windows":
        ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "windows", "ffmpeg.exe")
    else:
        ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "macos", "ffmpeg")

    if platform.system() != "Windows":
        os.chmod(ffmpeg_path, 0o755)

    command = f'"{ffmpeg_path}" -i "{video_file_path}" -ac 1 -ar 16000 -vn "{output_audio_path}"'
    os.system(command)

# Function to transcribe audio using Vosk
def transcribe_audio(audio_file_path):
    model = Model(MODEL_PATH)
    wf = wave.open(audio_file_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError("Audio file must be WAV format mono PCM.")
    
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    transcript = []
    
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        
        if rec.AcceptWaveform(data):
            result = rec.Result()
            text = json.loads(result)['text']
            transcript.append(text)
    
    final_transcript = " ".join(transcript)
    return final_transcript

# Function to handle the full transcription process
def transcribe_file():
    try:
        select_file_button.config(state=tk.DISABLED)
        
        file_path = filedialog.askopenfilename(title="Select an audio or video file", filetypes=[("Audio/Video Files", "*.wav *.mp4")])
        
        if not file_path:
            select_file_button.config(state=tk.NORMAL)
            return
        
        temp_audio_path = None
        
        if file_path.endswith(".mp4"):
            temp_audio_path = "temp_extracted_audio.wav"
            extract_audio_from_video(file_path, temp_audio_path)
            file_path = temp_audio_path  

        transcript = transcribe_audio(file_path)
        
        save_transcript_path = filedialog.asksaveasfilename(title="Save Transcript as", defaultextension=".txt")
        with open(save_transcript_path, "w") as f:
            f.write(transcript)
        
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        messagebox.showinfo("Success", "Transcription completed successfully!")
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    
    finally:
        select_file_button.config(state=tk.NORMAL)

# Function to start the transcription process in a separate thread
def start_transcription():
    thread = threading.Thread(target=transcribe_file)
    thread.start()

# Tkinter GUI setup
root = tk.Tk()
root.title("JTA - Beetroot (1.0)")
root.geometry("600x400")

select_file_button = ttk.Button(root, text="Select File and Transcribe", command=start_transcription)
select_file_button.pack(pady=20)

root.mainloop()
