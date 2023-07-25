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

# i = 0
# temp = list('[>=========]')
def animate_dots():
#     global i
#     global temp
#     backup = loading_label['text']
    
#     temp[i+1] = '='
#     temp[i+2] = '>'
#     temp = ''.join(temp)
#     loading_label['text'] += temp

    
#     i+=1
#     if i == 10:
#         i = 0
#         temp = list('[>=========]')
    
    loading_label['text'] 
    dots = loading_label['text'].count('.')
    if dots < 3:
        loading_label['text'] += '.'
    else:
        loading_label['text'] = 'Estimating'
    root.after(500, animate_dots) 
    
def load_and_display_frame(filepath):
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

def drop(event):
    global file_path
    file_path = event.data
    load_and_display_frame(file_path)
    file_label.config(text=f'Loaded file: {file_path}')
    start_button.config(state=tk.NORMAL)

def open_file_explorer():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
    if file_path:
        load_and_display_frame(file_path)
        # file_label.config(text=f'Loaded file: {file_path}')
        file_label.config(text=f'Loaded file: done') # 크기가 계속 깨져서 수정
        start_button.config(state=tk.NORMAL)

def start_analysis_thread():
    thread = threading.Thread(target=start_analysis)
    thread.start()

def add_label_to_grid(row, column, text):
    labels_info[(row, column)] = text
    label = tk.Label(grid_frame, text=text, font=('Arial', 14))
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
            #각 5초마다 분석결과를 넣어줌.
            total_count = np.append(total_count,count)
            total_hand = np.append(total_hand,hand)
            total_depth = np.append(total_depth,depth)
            total_release = np.append(total_release,release)
            
        loading_label.pack_forget()

                # Remove existing labels from the grid_frame
        for widget in grid_frame.winfo_children():
            widget.destroy()

        # Add new labels to the grid_frame
        for i in range(7):
            for j in range(5):
                label_text = labels_info.get((i, j), '')
                label = tk.Label(grid_frame, text=label_text, font=('Arial', 14))
                label.grid(row=i, column=j, padx=5, pady=5)
                grid_frame.columnconfigure(j, weight=1)
                grid_frame.rowconfigure(i, weight=1)
        for i in range(1,7):
            if i < 6:
                add_label_to_grid(i,1,total_count[i-1])
                add_label_to_grid(i,2,total_hand[i-1])
                add_label_to_grid(i,3,f'{total_depth[i-1]} mm')
                add_label_to_grid(i,4,total_release[i-1])
            if i == 6: # 총점 평균
                add_label_to_grid(i,1,np.mean(total_count))
                add_label_to_grid(i,2,Counter(total_hand).most_common(1)[0][0])
                add_label_to_grid(i,3,f'{np.round(np.mean(total_depth),2)} mm')
                add_label_to_grid(i,4,Counter(total_release).most_common(1)[0][0])

    else:
        print('No file loaded.')

import tkinter as tk

labels_info = {
    (0, 0): '시간',
    (0, 1): '압박 횟수',
    (0, 2): '손 위치',
    (0, 3): '압박 깊이',
    (0, 4): '완전이완여부',
    (1, 0): '5~10초',
    (2, 0): '10~15초',
    (3, 0): '15~20초',
    (4, 0): '20~25초',
    (5, 0): '25~30초',    
    (6, 0): '평균',
}


root = TkinterDnD.Tk()
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)
root.title("HQC Estimator")
root.geometry('600x700')
root.resizable(True, True) 

# Apply ttk theme
style = ttk.Style()
style.theme_use('clam')

button_frame = tk.Frame(root)
button_frame.pack(fill=tk.BOTH, pady=10)

browse_button = ttk.Button(button_frame, text='Select File', command=open_file_explorer)
browse_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

start_button = ttk.Button(button_frame, text='Start Analysis', command=start_analysis_thread, state=tk.DISABLED)
start_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

drop_frame = tk.Frame(root, bd=2, relief='groove', bg='#dddddd')
drop_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

file_label = tk.Label(drop_frame, text='Drag and Drop Video File Here or Select a File', bg='#dddddd', fg='#333333', font=('Helvetica', 14))
file_label.pack(fill=tk.BOTH, expand=True)  

image_label = tk.Label(root)
image_label.pack(fill=tk.BOTH, expand=True)

loading_label = tk.Label(root, text='', font=('Arial', 30))
loading_label.pack(fill=tk.BOTH, expand=True)  

grid_frame = tk.Frame(root)
grid_frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()
