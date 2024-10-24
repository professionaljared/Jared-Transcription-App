import customtkinter as ctk  # Import customtkinter for modern themes
from PIL import Image, ImageTk  # Import Pillow
import os
import sys

# Attributes for the version name and number
version_name = "Ginger"
version_number = "1.3"
app_background_color = "#EBEBEB"  # Background color for the entire app
accent_color = "#E9A365"  # Main color of the version/ accent color for the app

def initialize_ui(transcribe_file_command, settings_command):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  # In bundled app
    else:
        base_path = os.path.dirname(__file__)

    # Set appearance mode and color theme for customtkinter
    ctk.set_appearance_mode("light")  # Modes: "light", "dark", or "system"
    ctk.set_default_color_theme("green")  # Themes: "blue", "green", "dark-blue"

    # Create the root window
    root = ctk.CTk()  # Create a customtkinter window
    root.title(f"JTA - {version_name} ({version_number})")
    root.geometry("600x400")

    # Create a main frame to organize widgets
    main_frame = ctk.CTkFrame(root, corner_radius=15)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    # Add a label to welcome users
    welcome_label = ctk.CTkLabel(main_frame, text=f"Welcome to JTA - {version_name} ({version_number})", font=ctk.CTkFont(size=20, weight="bold"), text_color=accent_color)
    welcome_label.grid(row=0, column=0, padx=10, pady=10)

    # Add a button for selecting a file and transcribing
    select_file_button = ctk.CTkButton(main_frame, text="Select File and Transcribe", command=transcribe_file_command, fg_color=accent_color)
    select_file_button.grid(row=1, column=0, padx=10, pady=20)
    select_file_button.configure(hover_color="#9c6d43")

    # Add a progress bar
    progress_bar = ctk.CTkProgressBar(main_frame, width=400, progress_color=accent_color)
    progress_bar.grid(row=2, column=0, padx=10, pady=10)
    progress_bar.set(0)  # Initialize the progress bar to 0

    # Add a label to show progress percentage
    progress_label = ctk.CTkLabel(main_frame, text="Awaiting File...", font=ctk.CTkFont(size=12))
    progress_label.grid(row=3, column=0, padx=10, pady=5)

    # Resize gear icon using PIL
    gear_icon_path = os.path.join(base_path, "icons", "gear_icon.png")
    gear_image = Image.open(gear_icon_path)

    # Resize the image
    gear_image_resized = gear_image.resize((30, 30), Image.LANCZOS)

    # Convert the resized image to PhotoImage
    gear_icon = ctk.CTkImage(light_image=gear_image_resized, dark_image=gear_image_resized, size=(30, 30))

    # Add gear icon button for settings
    settings_button = ctk.CTkButton(root, image=gear_icon, text="", command=settings_command, width=40, height=40, fg_color="transparent")
    settings_button.image = gear_icon  # Keep a reference to avoid garbage collection
    settings_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

    # Ensure the window expands correctly
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    return root, select_file_button, progress_bar, progress_label

