import os
import wave
import json
import shutil
import subprocess
import sys
from tkinter import filedialog, messagebox  # Using filedialog and messagebox from tkinter for simplicity
import threading
import concurrent.futures
from vosk import Model, KaldiRecognizer
from jta_ui import initialize_ui  # UI Import

def get_documents_folder():
    return os.path.join(os.environ['USERPROFILE'], 'Documents')

def get_temp_audio_path():
    documents_folder = get_documents_folder()
    temp_audio_folder = os.path.join(documents_folder, "JTA - Jared Transcription App")
    os.makedirs(temp_audio_folder, exist_ok=True)
    return os.path.join(temp_audio_folder, "temp_extracted_audio.wav")

# Get the ffmpeg path
def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        ffmpeg_path = os.path.join(base_path, "ffmpeg", "windows", "ffmpeg.exe")
    else:
        ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "windows", "ffmpeg.exe")

    return ffmpeg_path

# Extract audio from video using ffmpeg
def extract_audio_from_video(video_file_path, output_audio_path):
    ffmpeg_path = get_ffmpeg_path()
    progress_label.configure(text="Processing Audio...")
    progress_bar.configure(mode='indeterminate')
    progress_bar.start()

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
        progress_label.configure(text="Audio extraction completed successfully.")
        print("Audio extraction completed successfully.")
        progress_bar.stop()  # Stop the indeterminate progress bar
        progress_bar.configure(mode='determinate')
        progress_bar.set(1.0)
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
    progress_label.configure(text="Starting transcription, please wait...")
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)

    model_path = os.path.join(base_path, "model/vosk-model-en-us-0.22")

    if not os.path.exists(model_path):
        raise FileNotFoundError("Vosk model directory not found. Please make sure the model is included with the application.")

    model = Model(model_path)
    wf = wave.open(audio_file_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError("Audio file must be WAV format mono PCM.")

    total_frames = wf.getnframes()
    chunk_size = 16000 * 45  # 60 seconds per chunk
    chunks = []

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
            progress_bar.set(progress / 100)
            progress_label.configure(text=f"Processing: {int(progress)}%")
            root.update_idletasks()

    transcript.sort(key=lambda x: x[0])
    final_transcript = " ".join([text for _, text in transcript])
    return final_transcript

# File selection and transcription function
def transcribe_file():
    try:
        select_file_button.configure(state="disabled")
        progress_bar.set(0)
        progress_label.configure(text="Selecting File...")

        file_path = filedialog.askopenfilename(title="Select an audio or video file", filetypes=[("Audio/Video Files", "*.wav *.mp4")])

        if not file_path:
            select_file_button.configure(state="normal")
            progress_label.configure(text="Awaiting File...")
            return

        documents_folder = os.path.join(os.getenv('USERPROFILE'), 'Documents')
        temp_audio_folder = os.path.join(documents_folder, "JTA - Jared Transcription App")
        if not os.path.exists(temp_audio_folder):
            os.makedirs(temp_audio_folder)

        temp_audio_path = os.path.join(temp_audio_folder, "temp_extracted_audio.wav")

        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        if file_path.endswith(".mp4"):
            extract_audio_from_video(file_path, temp_audio_path)
            file_path = temp_audio_path

        transcript = transcribe_audio(file_path)

        save_transcript_path = filedialog.asksaveasfilename(initialfile="Untitled", title="Save Transcript as", defaultextension=".txt")
        if save_transcript_path:
            with open(save_transcript_path, "w") as f:
                f.write(transcript)

        temp_audio_path = get_temp_audio_path()
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        messagebox.showinfo("Success", "Transcription completed successfully!")
        progress_label.configure(text="Transcription completed!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        progress_label.configure(text="An error occurred.")

    finally:
        select_file_button.configure(state="normal")

def start_transcription():
    thread = threading.Thread(target=transcribe_file)
    thread.start()

# CustomTkinter GUI setup
root, select_file_button, progress_bar, progress_label = initialize_ui(
    transcribe_file_command=start_transcription
)

if __name__ == "__main__":
    root.mainloop()
