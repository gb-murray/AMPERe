import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import json
import threading

def generate_config():
    image_path = entry_image_path.get()
    if image_path:
        thread = threading.Thread(target=run_imped, args=(image_path,))
        thread.start()
    else:
        messagebox.showwarning("Warning", "Please select an image first.")

def run_imped(image_path):
    subprocess.run(["python", "processing/imped.py", image_path])
    messagebox.showinfo("Success", "Configuration generated successfully!")

def load_config():
    config_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if config_path:
        with open(config_path, 'r') as file:
            config = json.load(file)
        scale_gaussian.set(config.get('gaussian', 0))
        scale_thresh.set(config.get('threshold', 0))
        scale_open.set(config.get('open', 0))
        scale_close.set(config.get('close', 0))
        messagebox.showinfo("Success", "Configuration loaded successfully!")

def save_config():
    config = {
        "gaussian": int(scale_gaussian.get()),
        "threshold": int(scale_thresh.get()),
        "open": int(scale_open.get()),
        "close": int(scale_close.get())
    }
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)
    messagebox.showinfo("Success", "Configuration saved successfully!")
    config_window.destroy()
    open_processing_window()

def browse_image():
    filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
    entry_image_path.delete(0, tk.END)
    entry_image_path.insert(0, filename)

def open_config_window():
    global config_window, scale_gaussian, scale_thresh, scale_open, scale_close
    config_window = tk.Toplevel(window)
    config_window.title("Generate Configuration")

    tk.Label(config_window, text="Image Path:").grid(row=0, column=0, padx=10, pady=10)
    global entry_image_path
    entry_image_path = tk.Entry(config_window, width=50)
    entry_image_path.grid(row=0, column=1, padx=10, pady=10)
    btn_browse_image = tk.Button(config_window, text="Browse", command=browse_image)
    btn_browse_image.grid(row=0, column=2, padx=10, pady=10)

    tk.Button(config_window, text="Generate Configuration", command=generate_config).grid(row=1, column=1, padx=10, pady=10)
    tk.Button(config_window, text="Load Existing Configuration", command=load_config).grid(row=2, column=1, padx=10, pady=10)

    tk.Label(config_window, text="Gaussian:").grid(row=3, column=0, padx=10, pady=10)
    tk.Label(config_window, text="Threshold:").grid(row=4, column=0, padx=10, pady=10)
    tk.Label(config_window, text="Open:").grid(row=5, column=0, padx=10, pady=10)
    tk.Label(config_window, text="Close:").grid(row=6, column=0, padx=10, pady=10)

    scale_gaussian = tk.Scale(config_window, from_=0, to=100, orient=tk.HORIZONTAL)
    scale_thresh = tk.Scale(config_window, from_=0, to=255, orient=tk.HORIZONTAL)
    scale_open = tk.Scale(config_window, from_=0, to=100, orient=tk.HORIZONTAL)
    scale_close = tk.Scale(config_window, from_=0, to=100, orient=tk.HORIZONTAL)

    scale_gaussian.grid(row=3, column=1, padx=10, pady=10)
    scale_thresh.grid(row=4, column=1, padx=10, pady=10)
    scale_open.grid(row=5, column=1, padx=10, pady=10)
    scale_close.grid(row=6, column=1, padx=10, pady=10)

    tk.Button(config_window, text="Save Configuration and Continue", command=save_config).grid(row=7, column=1, padx=10, pady=10)

def process_images():
    input_dir = entry_input_dir.get()
    if input_dir:
        config_file = "config.json"
        output_dir = entry_output_dir.get() if entry_output_dir.get() else None
        subprocess.run(["python", "processing/amped.py", input_dir, "-o", output_dir, "-c", config_file])
        messagebox.showinfo("Success", "Image processing completed!")
    else:
        messagebox.showwarning("Warning", "Please select an input directory.")

def browse_input_dir():
    dirname = filedialog.askdirectory()
    entry_input_dir.delete(0, tk.END)
    entry_input_dir.insert(0, dirname)

def browse_output_dir():
    dirname = filedialog.askdirectory()
    entry_output_dir.delete(0, tk.END)
    entry_output_dir.insert(0, dirname)

def open_processing_window():
    processing_window = tk.Toplevel(window)
    processing_window.title("Process Images")

    tk.Label(processing_window, text="Input Directory:").grid(row=0, column=0, padx=10, pady=10)
    global entry_input_dir
    entry_input_dir = tk.Entry(processing_window, width=50)
    entry_input_dir.grid(row=0, column=1, padx=10, pady=10)
    btn_browse_input = tk.Button(processing_window, text="Browse", command=browse_input_dir)
    btn_browse_input.grid(row=0, column=2, padx=10, pady=10)

    tk.Label(processing_window, text="Output Directory (optional):").grid(row=1, column=0, padx=10, pady=10)
    global entry_output_dir
    entry_output_dir = tk.Entry(processing_window, width=50)
    entry_output_dir.grid(row=1, column=1, padx=10, pady=10)
    btn_browse_output = tk.Button(processing_window, text="Browse", command=browse_output_dir)
    btn_browse_output.grid(row=1, column=2, padx=10, pady=10)

    tk.Button(processing_window, text="Process Images", command=process_images).grid(row=2, column=1, padx=10, pady=10)

# Main window
window = tk.Tk()
window.title("AMPERe")

btn_open_config_window = tk.Button(window, text="Generate Configuration", command=open_config_window)
btn_open_config_window.pack(pady=20)

window.mainloop()
