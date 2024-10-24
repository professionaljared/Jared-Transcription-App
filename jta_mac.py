import os
import wave
import json
import shutil
import subprocess
import sys
import tkinter as tk
import threading
from tkinter import filedialog, messagebox
from vosk import Model, KaldiRecognizer
from jta_ui import initialize_ui # UI Import

def get_documents_folder():
    return os.path.join(os.environ['HOME'], 'Documents')

def get_temp_audio_path():
    documents_folder = get_documents_folder()
    temp_audio_folder = os.path.join(documents_folder, "JTA - Jared Transcription App")
    os.makedirs(temp_audio_folder, exist_ok=True)
    return os.path.join(temp_audio_folder, "temp_extracted_audio.wav")

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        ffmpeg_path = os.path.join(base_path, "ffmpeg", "macos", "ffmpeg")
    else:
        ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "macos", "ffmpeg")
    return ffmpeg_path

def extract_audio_from_video(video_file_path, output_audio_path, extraction_done_callback):
    ffmpeg_path = get_ffmpeg_path()
    progress_label.configure(text="Processing Audio...")
    progress_bar.set(0)
    progress_bar.configure(mode='indeterminate')
    progress_bar.start()  # Start the indeterminate progress animation

    os.chmod(ffmpeg_path, 0o755)

    command = [
        ffmpeg_path,
        '-i', video_file_path,
        '-ac', '1',
        '-ar', '16000',
        '-vn',
        '-preset', 'ultrafast',
        output_audio_path
    ]

    def run_ffmpeg():
        try:
            subprocess.run(command, check=True)
            progress_label.configure(text="Audio extraction completed successfully.")
            print("Audio extraction completed successfully.")
            progress_bar.stop()  # Stop the indeterminate progress bar
            progress_bar.configure(mode='determinate')
            progress_bar.set(1.0)  # Set progress bar to 100% after completion
            extraction_done_callback(output_audio_path)
        except subprocess.CalledProcessError as e:
            progress_label.configure(text="Failed to extract audio.")
            print(f"Failed to extract audio. Command: {command}")
        except Exception as e:
            progress_label.configure(text="An error occurred during extraction.")
            print(f"Error during extraction: {e}")
        finally:
            progress_bar.stop()
            progress_bar.configure(mode='determinate')

    threading.Thread(target=run_ffmpeg).start()

# File selection and transcription function
def transcribe_audio(audio_file_path):
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
    
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    transcript = []
    total_frames = wf.getnframes()
    processed_frames = 0

    def update_progress():
        progress = (processed_frames / total_frames) * 100
        progress_bar.set(progress / 100)
        progress_label.configure(text=f"Transcribing: {int(progress)}%")
        root.update_idletasks()

    while True:
        data = wf.readframes(64000)
        if len(data) == 0:
            break
        
        processed_frames += len(data) // wf.getsampwidth()
        if int((processed_frames / total_frames) * 100) > int(((processed_frames - len(data)) / total_frames) * 100):
            root.after(0, update_progress)  # Update progress for each 1%

        if rec.AcceptWaveform(data):
            result = rec.Result()
            text = json.loads(result)['text']
            transcript.append(text)
    
    final_transcript = " ".join(transcript)
    return final_transcript

def transcribe_and_save(file_path):
    # Start the transcription in a new thread to keep UI responsive
    transcription_thread = threading.Thread(target=transcribe_audio_and_save_thread, args=(file_path,))
    transcription_thread.start()

def transcribe_audio_and_save_thread(file_path):
    try:
        progress_label.configure(text="Transcribing audio, please wait...")
        transcript = transcribe_audio(file_path)

        save_transcript_path = filedialog.asksaveasfilename(initialfile="Untitled", title="Save Transcript as", defaultextension=".txt")
        if save_transcript_path:
            with open(save_transcript_path, "w") as f:
                f.write(transcript)

        progress_label.configure(text="Transcription completed successfully.")
        messagebox.showinfo("Success", "Transcription completed successfully!")
        select_file_button.configure(state=tk.NORMAL, fg_color="#E9A365")
        temp_audio_path = get_temp_audio_path()
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

    except Exception as e:
        progress_label.configure(text="An error occurred during transcription.")
        messagebox.showerror("Error", f"An error occurred during transcription: {e}")

def transcribe_file():
    try:
        select_file_button.configure(state=tk.DISABLED, fg_color="#9c6d43")
        progress_bar.set(0)

        file_path = filedialog.askopenfilename(title="Select an audio or video file", filetypes=[("Audio/Video Files", "*.wav *.mp4")])
        progress_label.configure(text="Selecting File...")
        if not file_path:
            select_file_button.configure(state=tk.NORMAL, fg_color="#E9A365")
            progress_label.configure(text="Awaiting File...")
            return

        temp_audio_path = get_temp_audio_path()

        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        if file_path.endswith(".mp4"):
            # Extract audio from video and then transcribe
            extract_audio_from_video(file_path, temp_audio_path, extraction_done_callback=transcribe_and_save)
        else:
            # Transcribe directly if it's an audio file
            transcribe_and_save(file_path)

    except Exception as e:
        progress_label.configure(text="An error occurred.")
        messagebox.showerror("Error", f"An error occurred: {e}")

def open_settings_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x200")

root, select_file_button, progress_bar, progress_label = initialize_ui(
    transcribe_file_command=lambda: threading.Thread(target=transcribe_file).start(),
    settings_command=open_settings_window
)

if __name__ == "__main__":
    root.mainloop()