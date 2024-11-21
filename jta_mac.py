import os
import sys
import subprocess
import ssl
import whisper
import tqdm
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from jta_ui import initialize_ui, accent_color, dark_accent_color # UI Import

# token bypass
ssl._create_default_https_context = ssl._create_unverified_context

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

def extract_audio_from_video(video_file_path, output_audio_path):
    ffmpeg_path = get_ffmpeg_path()
    progress_label.configure(text="Processing Audio...")
    progress_bar.configure(mode='indeterminate')
    progress_bar.start()  

    os.chmod(ffmpeg_path, 0o755)

    # This will be proccessed again via Whisper, do not break down the quality too much
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
        progress_label.configure(text="Audio extraction complete. Waiting to Transcribe...")
        print("Audio extraction completed successfully.")
        progress_bar.stop()  
        progress_bar.configure(mode='determinate')
        progress_bar.set(1.0)
    except subprocess.CalledProcessError as e:
        print(f"Failed to extract audio. Command: {command}")
        raise e

# Monkey-patch tqdm to capture progress
class TqdmPatch(tqdm.std.tqdm):
    def update(self, n=1):
        super().update(n)
        progress = self.n / float(self.total) if self.total else 0
        progress_bar.set(progress)
        progress_label.configure(text=f"Transcribing... {int(progress * 100)}%")
        root.update_idletasks()

# Transcribe audio using Whisper
def transcribe_audio(audio_file_path):
    model = whisper.load_model("base")  # "tiny", "small", "medium", "large"; default is base
    print("Transcribing, please wait...")
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"The file {audio_file_path} was not found.")

    progress_bar.configure(mode='determinate')

    # Monkey-patch tqdm to update the progress bar
    original_tqdm = tqdm.tqdm
    tqdm.tqdm = TqdmPatch

    try:
        result = model.transcribe(audio_file_path, verbose=False)
        transcript = result['text']
    finally:
        # Restore the original tqdm
        tqdm.tqdm = original_tqdm

    return transcript

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

        documents_folder = os.path.join(os.getenv('USERPROFILE', os.getenv('HOME')), 'Documents')
        temp_audio_folder = os.path.join(documents_folder, "JTA - Jared Transcription App")
        if not os.path.exists(temp_audio_folder):
            os.makedirs(temp_audio_folder)

        temp_audio_path = os.path.join(temp_audio_folder, "temp_extracted_audio.wav")

        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        if file_path.endswith(".mp4"):
            extract_audio_from_video(file_path, temp_audio_path)
            file_path = temp_audio_path

        # Temporarily update system PATH to prioritize custom ffmpeg
        original_path = os.environ.get("PATH", "")
        ffmpeg_dir = os.path.dirname(get_ffmpeg_path())
        os.environ["PATH"] = f"{ffmpeg_dir}{os.pathsep}{original_path}"

        transcript = transcribe_audio(file_path)

        # Restore the original PATH
        os.environ["PATH"] = original_path

        save_transcript_path = filedialog.asksaveasfilename(initialfile="Untitled", title="Save Transcript as", defaultextension=".txt")
        if save_transcript_path:
            with open(save_transcript_path, "w", encoding="utf-8") as f:
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

root, select_file_button, progress_bar, progress_label = initialize_ui(
    transcribe_file_command=lambda: threading.Thread(target=transcribe_file).start(),
)

if __name__ == "__main__":
    root.mainloop()