import os
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading

# Define default paths for input and output folders
default_folders = {
    "Effects": {
        "input": f"C:\\Users\\{os.environ['USERNAME']}\\Documents\\Image-Line\\FL Studio\\Presets\\Plugin database\\Installed\\Effects",
        "output": f"C:\\Users\\{os.environ['USERNAME']}\\Documents\\Image-Line\\FL Studio\\Presets\\Plugin database\\Effects",
    },
    "Generators": {
        "input": f"C:\\Users\\{os.environ['USERNAME']}\\Documents\\Image-Line\\FL Studio\\Presets\\Plugin database\\Installed\\Generators",
        "output": f"C:\\Users\\{os.environ['USERNAME']}\\Documents\\Image-Line\\FL Studio\\Presets\\Plugin database\\Generators",
    },
}


# Function to get default paths based on the selected type
def get_default_paths(selected_type):
    return (
        default_folders[selected_type]["input"],
        default_folders[selected_type]["output"],
    )


# GUI Functions for selecting folders
def select_folder(entry):
    folder = filedialog.askdirectory(initialdir=entry.get(), title="Select Folder")
    if folder:  # Only update the entry if a folder is selected
        entry.delete(0, tk.END)
        entry.insert(0, folder)


# Function to log messages in the GUI
def log_message(message, color="black"):
    output_textbox.config(state=tk.NORMAL)  # Make the textbox editable
    output_textbox.insert(tk.END, message + "\n", ("colored",))
    output_textbox.tag_config("colored", foreground=color)
    output_textbox.config(state=tk.DISABLED)  # Make the textbox non-editable


# Function to read the vendor name from a binary file
def read_vendor_name(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            index = data.rfind(b"\x00" * 7)  # Look for the 7 null bytes
            if index != -1 and index + 7 < len(data):
                return data[index + 7 :].decode().strip()
    except Exception as e:
        print(f"Error reading vendor name from {file_path}: {e}")
    return None


# Function to determine the vendor name based on file location
def get_vendor_name(file_path):
    vendor_name = read_vendor_name(file_path) or (
        "Fruity" if "Fruity" in os.path.dirname(file_path) else "Unknown"
    )
    return vendor_name


# Main plugin organization process
def organize_plugins():
    input_folder = input_folder_entry.get()
    output_folder = output_folder_entry.get()

    if not os.path.isdir(input_folder) or not os.path.isdir(output_folder):
        messagebox.showerror("Error", "Please select valid input and output folders.")
        return

    log_message(f"Selected Input Folder: {input_folder}", "blue")
    log_message(f"Selected Output Folder: {output_folder}", "blue")

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".fst"):  # Check for .fst files
                file_path = os.path.join(root, file)
                vendor_name = get_vendor_name(file_path)  # Use the new function
                try:
                    copied_file = copy_to_vendor_folder(
                        file_path, vendor_name, output_folder
                    )
                    log_message(f"[COPIED] '{file}' to '{copied_file}'", "#197ee3")
                except Exception as e:
                    log_message(f"[ERROR] Failed to copy '{file}': {str(e)}", "red")

    messagebox.showinfo("Completed", "Plugin organization completed successfully!")


# Function to copy a file to a new folder named after the vendor
def copy_to_vendor_folder(file_path, vendor_name, output_folder):
    new_folder = os.path.join(output_folder, vendor_name)
    os.makedirs(new_folder, exist_ok=True)  # Create the folder if it doesn't exist
    new_file = os.path.join(new_folder, os.path.basename(file_path))
    shutil.copy(file_path, new_file)
    return new_file


# Function to update folder paths based on the selected type
def update_paths(*args):
    selected_type = type_var.get()
    input_folder, output_folder = get_default_paths(selected_type)
    input_folder_entry.delete(0, tk.END)
    input_folder_entry.insert(0, input_folder)
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, output_folder)


# Function to run organizing in a separate thread
def start_organizing():
    thread = threading.Thread(target=organize_plugins)
    thread.start()


# Create the GUI window
root = tk.Tk()

# Determine base path for assets
if getattr(sys, 'frozen', False):
    # Running in a bundle
    base_path = sys._MEIPASS  # This is where PyInstaller unpacks the files
else:
    # Running in a normal Python environment
    base_path = os.path.dirname(os.path.abspath(__file__))

# Load the azure.tcl theme file
azure_tcl_path = os.path.join(base_path, "assets", "azure.tcl")
root.tk.call("source", azure_tcl_path)

# Set the theme (ensure dark theme file is also included)
root.tk.call("set_theme", "dark")
root.title("FL Studio Vendor-Based Plugin Organizer")
root.geometry("950x750")


# Standard UI elements creation
def create_label(parent, text, font_size=None, font_weight=None):
    if font_size or font_weight:
        label = ttk.Label(
            parent, text=text, font=(root, font_size or 12, font_weight or "normal")
        )
        label.pack(pady=20)
    else:
        label = ttk.Label(parent, text=text)  # Default label style
        label.pack(pady=10)


def create_entry_with_button(parent, label_text, button_command):
    frame = ttk.Frame(parent)
    frame.pack(fill="x", padx=20, pady=10)
    ttk.Label(frame, text=label_text).pack(side="left")
    entry = ttk.Entry(frame)
    entry.pack(side="left", fill="x", expand=True, padx=5)
    button = ttk.Button(frame, text="Open", command=button_command)
    button.pack(side="right")
    return entry


# Create UI elements
create_label(
    root, "FL Studio Vendor-Based Plugin Organizer", font_size=20, font_weight="bold"
)

# Author Frame
footer_frame = ttk.Frame(root)
footer_frame.pack(side="bottom", fill="x", pady=6)

colors = ["#7a91ff", "#FFFF00", "#FF0000", "#00FF00", "#a282fa", "#FFA500"]


# Function to create a multi-colored author label
def create_colored_label(parent, text):
    text_widget = tk.Text(parent, height=1, width=len(text), bd=0, wrap=tk.NONE)
    text_widget.pack(side="right", padx=10)

    # Insert colored characters
    for i, char in enumerate(text):
        color = colors[i % len(colors)]
        text_widget.insert(tk.END, char, (color,))
        text_widget.tag_configure(color, foreground=color)

    text_widget.config(state=tk.DISABLED)


# Add your author name label with alternating colors
create_colored_label(footer_frame, "sitayo")


def create_red_text(parent, text):
    label = tk.Label(
        parent,
        text=text,
        fg="#fc4952",  # Red color for the text
    )
    label.pack(pady=10)  # Adjust padding as needed


# Create the red text message under the title
create_red_text(
    root,
    "Defaults are preselected and recommended.\n"
    "Changes are optional but typically unnecessary unless your files aren't on the C: drive.\n\n"
    "This supports FL Studio 21's Effects & Generators Folder structure at least, unsure of other versions file structures.",
)


type_var = tk.StringVar(value="Effects")
type_menu = ttk.Combobox(
    root, textvariable=type_var, state="readonly", values=("Effects", "Generators")
)
type_menu.pack(pady=10)
type_menu.bind("<<ComboboxSelected>>", update_paths)

input_folder_entry = create_entry_with_button(
    root, "Input Folder:", lambda: select_folder(input_folder_entry)
)
output_folder_entry = create_entry_with_button(
    root, "Output Folder:", lambda: select_folder(output_folder_entry)
)

start_button = ttk.Button(root, text="Organize Plugins", command=start_organizing)
start_button.pack(pady=20)

create_label(root, "Logs:")

# Frame for log output
log_frame = ttk.Frame(root)
log_frame.pack(fill="both", expand=True, padx=20, pady=2)
output_textbox = tk.Text(log_frame, wrap=tk.WORD, state=tk.DISABLED)
output_textbox.pack(side="left", fill="both", expand=True)
vertical_scrollbar = ttk.Scrollbar(
    log_frame, orient="vertical", command=output_textbox.yview
)
vertical_scrollbar.pack(side="right", fill="y")
output_textbox.config(yscrollcommand=vertical_scrollbar.set)

# Set default paths for input and output on startup
update_paths()

# Start the main GUI loop
root.mainloop()
