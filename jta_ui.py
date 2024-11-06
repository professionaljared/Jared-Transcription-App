import customtkinter as ctk  # Import customtkinter for modern themes
from PIL import Image 
import os
import sys

# Attributes for the version name and number
version_name = "Okra"
version_number = "2.0"
app_background_color = "#EBEBEB"  
accent_color = "#516426"  # Main color of the version
dark_accent_color = "#273012" # Mainly used for hovers

def initialize_ui(transcribe_file_command):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  # In bundled app
    else:
        base_path = os.path.dirname(__file__)

    # Set appearance mode and color theme for customtkinter
    ctk.set_appearance_mode("light")  # Modes: "light", "dark", or "system"
    ctk.set_default_color_theme("green")  # Themes: "blue", "green", "dark-blue"

    # Create the root window
    root = ctk.CTk()  
    root.title(f"JTA - {version_name} ({version_number})")
    root.geometry("600x400")

    # Create a main frame to organize widgets
    main_frame = ctk.CTkFrame(root, corner_radius=15)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    # Welcome Label
    welcome_label = ctk.CTkLabel(main_frame, text=f"Welcome to JTA - {version_name} ({version_number})", font=ctk.CTkFont(size=30, weight="bold"), text_color=accent_color)
    welcome_label.grid(row=0, column=0, padx=10, pady=10)

    # Add a button for selecting a file and transcribing
    select_file_button = ctk.CTkButton(main_frame, text="Select File and Transcribe", command=transcribe_file_command, fg_color=accent_color)
    select_file_button.grid(row=1, column=0, padx=10, pady=20)
    select_file_button.configure(hover_color=dark_accent_color)

    # Add a progress bar
    progress_bar = ctk.CTkProgressBar(main_frame, width=400, progress_color=accent_color)
    progress_bar.grid(row=2, column=0, padx=10, pady=10)
    progress_bar.set(0)  

    # Add a label to show progress percentage
    progress_label = ctk.CTkLabel(main_frame, text="Awaiting File...", font=ctk.CTkFont(size=12))
    progress_label.grid(row=3, column=0, padx=10, pady=5)

    # Load and resize gear icon using PIL
    gear_icon_path = os.path.join(base_path, "icons", "gear_icon.png")
    try:
        gear_image = Image.open(gear_icon_path)
    except FileNotFoundError:
        print(f"Error: Could not find the gear icon at {gear_icon_path}. Make sure the file exists.")
        return root, select_file_button, progress_bar, progress_label

    gear_image_resized = gear_image.resize((30, 30), Image.LANCZOS)

    # Convert the resized image to CTkImage
    gear_icon = ctk.CTkImage(light_image=gear_image_resized, dark_image=gear_image_resized, size=(30, 30))

    # Add gear icon button for settings
    settings_button = ctk.CTkButton(main_frame, image=gear_icon, text="", width=40, height=40,
                                     fg_color='#dbdbdb', border_width=0, corner_radius=2, hover_color=accent_color)
    settings_button.configure(command=lambda: show_frame(settings_frame))
    settings_button.image = gear_icon
    settings_button.place(relx=1.0, rely=0.0, anchor="ne", x=-25, y=25)

    # Create the settings frame
    settings_frame = ctk.CTkFrame(root, corner_radius=15)
    settings_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    # Settings Page Header
    settings_label = ctk.CTkLabel(settings_frame, text="Settings", font=ctk.CTkFont(size=30, weight="bold"), text_color=accent_color)
    settings_label.grid(row=0, column=0, padx=10, pady=10)

    # Example settings 
    settings_option = ctk.CTkLabel(settings_frame, text="Example Setting: Toggle Dark Mode", font=ctk.CTkFont(size=12))
    settings_option.grid(row=1, column=0, padx=10, pady=10)

    toggle_mode_button = ctk.CTkButton(settings_frame, text="Toggle Dark Mode", command=lambda: dark_mode_toggle(), fg_color=accent_color, hover_color=dark_accent_color)
    toggle_mode_button.grid(row=2, column=0, padx=10, pady=10)
    
    def dark_mode_toggle():
        if ctk.get_appearance_mode() == "Light":
            settings_option.configure(text="Example Setting: Toggle Light Mode")
            toggle_mode_button.configure(text="Toggle Light Mode")
            ctk.set_appearance_mode("Dark")
            settings_button.configure(fg_color="#2b2b2b")
        else: 
            settings_option.configure(text="Example Setting: Toggle Dark Mode")
            toggle_mode_button.configure(text="Toggle Dark Mode")
            ctk.set_appearance_mode("Light")
            settings_button.configure(fg_color="#dbdbdb")
        
    # Back button to return to the main frame
    back_button = ctk.CTkButton(settings_frame, text="Back", command=lambda: show_frame(main_frame), fg_color=accent_color, hover_color=dark_accent_color)
    back_button.grid(row=3, column=0, padx=10, pady=20)

    # Function to switch between frames
    def show_frame(frame):
        frame.tkraise()

    # Initially show the main frame
    main_frame.tkraise()



    # Ensure the window expands correctly
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    settings_frame.grid_rowconfigure(0, weight=1)
    settings_frame.grid_columnconfigure(0, weight=1)

    return root, select_file_button, progress_bar, progress_label

