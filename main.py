import threading
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
from video_processing import process_video
from estimator import start_estimation
import cv2
from PIL import Image, ImageTk
import time

def drop(event):
    global file_path, file_label
    file_path = event.data
    file_label.config(text=f'Loaded file: {file_path}')  # change the label text to the file path
    start_button.config(state=tk.NORMAL)  # Enable the Start Analysis button

def open_file_explorer():
    global file_path, file_label
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])  # Open the file explorer
    if file_path:
        file_label.config(text=f'Loaded file: {file_path}')  # change the label text to the file path
        start_button.config(state=tk.NORMAL)  # Enable the Start Analysis button

def start_analysis_thread():
    start_button.config(state=tk.DISABLED)  # Disable the Start button while analysis is running
    thread = threading.Thread(target=start_analysis)
    thread.start()

def start_analysis():
    global file_path, loading_label
    if file_path:
        loading_label = tk.Label(root, text='Estimating...', font=('Arial', 36))
        loading_label.pack()
        root.update()  # update the root window to show the loading label
        critical_avg_image = process_video(file_path)  # Call the function with your video path
        critical_avg_image = cv2.convertScaleAbs(critical_avg_image) # 64bit --> 8bit
        critical_avg_image = cv2.cvtColor(critical_avg_image, cv2.COLOR_BGR2RGB)
        depth, release, hand = start_estimation(critical_avg_image)
        loading_label.pack_forget()  # remove the loading label

        # Update the result labels with the estimation results
        depth_label.config(text=f"Depth: {depth}")
        release_label.config(text=f"Release: {release}")
        hand_label.config(text=f"Hand: {hand}")
        start_button.config(state=tk.NORMAL)  # Enable the Start button after analysis is done
    else:
        print('No file loaded.')

file_path = None

root = TkinterDnD.Tk()
root.title("HQC Estimator")
root.geometry('1600x720')

style = ttk.Style()
style.configure('Groove.TFrame', relief='groove', borderwidth=2)


style.configure(".", font=('Arial', 18))  # Set a global font size
style.configure("TLabel", background="white")  # Set a white background for labels
style.configure("TButton", background="gray", foreground="white")  # Set a gray background and white text for buttons

title_label = ttk.Label(root, text='HQC Estimator', font=('Arial', 36))
title_label.pack(pady=10)

button_frame = ttk.Frame(root)
button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

browse_button = ttk.Button(button_frame, text='Select File', command=open_file_explorer)
browse_button.pack(side=tk.LEFT, padx=10)

start_button = ttk.Button(button_frame, text='Start Analysis', command=start_analysis_thread, state=tk.DISABLED)  # Start button is initially disabled
start_button.pack(side=tk.RIGHT, padx=10)

drop_frame = ttk.Frame(root, style='Groove.TFrame')
drop_frame.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)

file_label = ttk.Label(drop_frame, text='Drag and Drop Video File Here or Select a File')
file_label.pack(fill=tk.BOTH, expand=tk.YES)

# Add labels for displaying the estimation results
depth_label = ttk.Label(root, text='', font=('Arial', 36))
depth_label.pack(pady=10)
release_label = ttk.Label(root, text='', font=('Arial', 36))
release_label.pack(pady=10)
hand_label = ttk.Label(root, text='', font=('Arial', 36))
hand_label.pack(pady=10)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)

root.mainloop()
