import os
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import zipfile

MODEL_OPTIONS = {
    "Small English Model": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
    "Medium English Model": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
    "Large English Model": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.42.zip"
}

def download_model(url, output_dir):
    zip_path = os.path.join(output_dir, "model.zip")
    urllib.request.urlretrieve(url, zip_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    
    os.remove(zip_path)

def start_download():
    selected_model = model_var.get()
    if selected_model:
        url = MODEL_OPTIONS[selected_model]
        model_dir = os.path.join(os.getcwd(), "model")
        os.makedirs(model_dir, exist_ok=True)
        
        try:
            download_button.config(state=tk.DISABLED)
            progress_label.config(text="Downloading, please wait...")
            root.update_idletasks()

            download_model(url, model_dir)
            progress_label.config(text=f"{selected_model} downloaded successfully!")
            messagebox.showinfo("Download Complete", "Model downloaded successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during the download: {e}")
        
        finally:
            download_button.config(state=tk.NORMAL)

root = tk.Tk()
root.title("JTA - Beetroot Model Downloader")
root.geometry("400x200")

model_var = tk.StringVar()
model_label = ttk.Label(root, text="Select a Vosk Model:")
model_label.pack(pady=5)

model_dropdown = ttk.Combobox(root, textvariable=model_var, values=list(MODEL_OPTIONS.keys()), state="readonly")
model_dropdown.pack(pady=5)

download_button = ttk.Button(root, text="Download Selected Model", command=start_download)
download_button.pack(pady=10)

progress_label = ttk.Label(root, text="")
progress_label.pack(pady=5)

root.mainloop()
