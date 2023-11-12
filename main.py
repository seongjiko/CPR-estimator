import threading
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
from video_processing import process_video
from estimator import start_estimation
import cv2
from PIL import Image, ImageTk
import numpy as np
from collections import Counter
import time
import csv
import datetime

current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # 현재 날짜와 시간을 문자열로 변환

# save_path = f"C:/Users/CPR/Desktop/record_30sec/" # csv
save_path = f"C:/Users/MMC/Desktop/" # csv

def animate_dots():    
    loading_label['text'] 
    dots = loading_label['text'].count('.')
    if dots < 3:
        loading_label['text'] += '.'
    else:
        loading_label['text'] = 'Estimating'
    root.after(500, animate_dots) 
    
def load_and_display_frame(filepath):
    global file_path

    cap = cv2.VideoCapture(filepath)

    ret, frame = cap.read()
    cap.release()
    if ret:
        frame = cv2.resize(frame, (224, 224))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_image = Image.fromarray(frame)
        frame_image_tk = ImageTk.PhotoImage(frame_image)
        image_label.config(image=frame_image_tk)
        image_label.image = frame_image_tk  # Keep a reference to the image so it's not garbage collected

def export_grid_data_to_csv(grid_frame, filename): # make csv
    with open(filename, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Iterate through the rows and columns of grid_frame
        for row in range(grid_frame.grid_size()[1]):  # Rows
            row_data = []
            for column in range(grid_frame.grid_size()[0]):  # Columns
                label = grid_frame.grid_slaves(row=row, column=column)[0]  # Get the label widget
                text = label.cget('text')
                row_data.append(text)
            csv_writer.writerow(row_data)


def drop(event):
    global file_path
    file_path = event.data

    if file_path:
        load_and_display_frame(file_path)
        file_label.config(text=f'Loaded file: {file_path}')
        start_button.config(state=tk.NORMAL)

def open_file_explorer():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
    if file_path:
        load_and_display_frame(file_path)
        file_label.config(text=f'Loaded file: {file_path}')
        start_button.config(state=tk.NORMAL)

def start_analysis_thread():
    thread = threading.Thread(target=start_analysis)
    thread.start()

def add_label_to_grid(row, column, text, idx = None):
    labels_info[(row, column)] = text

    fontsize = 17 if idx == 8 else 14

    label = tk.Label(grid_frame, text=text, font=('Arial', fontsize))
    label.grid(row=row, column=column, padx=5, pady=5)
    grid_frame.columnconfigure(column, weight=1)
    grid_frame.rowconfigure(row, weight=1)

def start_analysis():
    global file_path, loading_label
    total_count = np.array(())
    total_hand = np.array(())
    total_depth = np.array(())
    total_release = np.array(())

    if file_path:
        loading_label = tk.Label(root, text='Estimating', font=('Arial', 30))
        loading_label.pack()
        root.after(500, animate_dots)  # Start the animation
        root.update()
        for start in range(145, 726, 145): # 145 290 435 580 725
            
            critical_avg_image, count = process_video(file_path, start)
            critical_avg_image = cv2.convertScaleAbs(critical_avg_image)
            critical_avg_image = cv2.cvtColor(critical_avg_image, cv2.COLOR_BGR2RGB)
            depth, release, hand = start_estimation(critical_avg_image)

            total_count = np.append(total_count,count)
            total_hand = np.append(total_hand,hand)
            total_depth = np.append(total_depth,depth)
            total_release = np.append(total_release,release)
            
        loading_label.pack_forget()

                # Remove existing labels from the grid_frame
        for widget in grid_frame.winfo_children():
            widget.destroy()

        # Add new labels to the grid_frame
        for i in range(9):
            for j in range(5):
                label_text = labels_info.get((i, j), '')
                fontsize = 17 if i == 0 or i == 8 else 14
                
                label = tk.Label(grid_frame, text=label_text, font=('Arial', fontsize))

                label.grid(row=i, column=j, padx=5, pady=5)
                grid_frame.columnconfigure(j, weight=1)
                grid_frame.rowconfigure(i, weight=1)

        for i in range(1,9):
            if i == 1: # 경계선
                add_label_to_grid(i,0,'------------------')
                add_label_to_grid(i,1,'------------------')
                add_label_to_grid(i,2,'------------------')
                add_label_to_grid(i,3,'------------------')
                add_label_to_grid(i,4,'------------------')

            elif i < 7:
                add_label_to_grid(i,1,f'{total_count[i-2]} BPM') # BPM 단위로 출력
                add_label_to_grid(i,2,total_hand[i-2]) 
                add_label_to_grid(i,3,f'{total_depth[i-2]} mm')
                add_label_to_grid(i,4,total_release[i-2])

            elif i == 7: # 경계선
                add_label_to_grid(i,0,'------------------')
                add_label_to_grid(i,1,'------------------')
                add_label_to_grid(i,2,'------------------')
                add_label_to_grid(i,3,'------------------')
                add_label_to_grid(i,4,'------------------')

            elif i == 8: # 총점 평균
                add_label_to_grid(i,1,f'{np.mean(total_count)} BPM', i)
                add_label_to_grid(i,2,Counter(total_hand).most_common(1)[0][0], i)
                add_label_to_grid(i,3,f'{np.round(np.mean(total_depth),2)} mm', i)
                add_label_to_grid(i,4,Counter(total_release).most_common(1)[0][0], i)

        export_grid_data_to_csv(grid_frame, f'{save_path}/{file_path.split("/")[-1]}.csv')
        print(file_path)

    else:
        print('No file loaded.')

import tkinter as tk

labels_info = {
    (0, 0): 'Times',
    (0, 1): 'Num of CCs',
    (0, 2): 'Hand position',
    (0, 3): 'Maximum depth of CCs',
    (0, 4): 'complete release of CCs',
    (2, 0): '5~10s',
    (3, 0): '10~15s',
    (4, 0): '15~20s',
    (5, 0): '20~25s',
    (6, 0): '25~30s',    
    (7, 0): '------------------',
    (8, 0): 'Overall (average)'
}


root = TkinterDnD.Tk()
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)
root.title("HQC Estimator")
root.geometry('1200x800')
root.resizable(True, True) 

# Apply ttk theme
style = ttk.Style()
style.theme_use('clam')
style.configure('big.TButton', font=('Arial', 20))

button_frame = tk.Frame(root)
button_frame.pack(fill=tk.BOTH, pady=10)

browse_button = ttk.Button(button_frame, text='Select File', command=open_file_explorer, style='big.TButton')
browse_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

start_button = ttk.Button(button_frame, text='Start Analysis', command=start_analysis_thread, state=tk.DISABLED, style='big.TButton')
start_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

drop_frame = tk.Frame(root, bd=2, relief='groove', bg='#dddddd')
drop_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

file_label = tk.Label(drop_frame, text='Drag and Drop Video File Here or Select a File', bg='#dddddd', fg='#333333', font=('Arial', 20))
file_label.pack(fill=tk.BOTH, expand=True)  

image_label = tk.Label(root)
image_label.pack(fill=tk.BOTH, expand=True)

loading_label = tk.Label(root, text='', font=('Arial', 30))
loading_label.pack(fill=tk.BOTH, expand=True)  

grid_frame = tk.Frame(root)
grid_frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()
