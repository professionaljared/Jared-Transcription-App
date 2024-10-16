import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # Import Pillow

# Attributes for the version name and number
version_name = "Ginger"
version_number = "1.3"
label_background_color = "#E9A365"

def initialize_ui(transcribe_file_command, settings_command):
    root = tk.Tk()
    root.title(f"JTA - {version_name} ({version_number})")
    root.geometry("600x400")

    # Create a ttk style and set a theme
    style = ttk.Style()
    style.theme_use("clam")

    # Configure a custom style for ttk labels
    style.configure("Custom.TLabel", background=f"{label_background_color}", foreground="black", font=("Helvetica", 12), padding=10)

    # Create a frame to organize widgets
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew")

    # Add a ttk label
    welcome_label = ttk.Label(main_frame, text=f"Welcome to JTA - {version_name} ({version_number})", style="Custom.TLabel")
    welcome_label.grid(row=0, column=0, padx=10, pady=10)

    # Add a ttk button for selecting a file and transcribing
    select_file_button = ttk.Button(main_frame, text="Select File and Transcribe", command=transcribe_file_command)
    select_file_button.grid(row=1, column=0, padx=10, pady=20)

    # Add a progress bar
    progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=500, mode="determinate")
    progress_bar.grid(row=2, column=0, padx=10, pady=10)

    # Add a label to show progress percentage
    progress_label = ttk.Label(main_frame, text="Awaiting File...", style="Custom.TLabel")
    progress_label.grid(row=3, column=0, padx=10, pady=5)

    # Resize gear icon using PIL
    gear_icon_path = "icons/gear_icon.png"  # Make sure to provide the correct path to your gear icon image
    gear_image = Image.open(gear_icon_path)

    # Resize the image (e.g., 24x24 pixels) using LANCZOS instead of ANTIALIAS
    gear_image_resized = gear_image.resize((24, 24), Image.LANCZOS)

    # Convert the resized image to PhotoImage
    gear_icon = ImageTk.PhotoImage(gear_image_resized)

    # Add gear icon button for settings
    settings_button = ttk.Button(root, image=gear_icon, command=settings_command)
    settings_button.image = gear_icon  # Keep a reference to avoid garbage collection
    settings_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

    # Ensure the window expands correctly
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    return root, select_file_button, progress_bar, progress_label

