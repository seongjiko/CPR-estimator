import threading
import tkinter as tk
from tkinter import ttk, Scrollbar, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from estimator import start_estimation
import cv2
from PIL import Image, ImageTk
import numpy as np
from collections import Counter
from threading import Thread, Event
import time
import csv
import datetime
current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # 현재 날짜와 시간을 문자열로 변환

event = Event() # 스레드 종료를 위함

save_path = f"C:/Users/MMC/Desktop/record/{current_time}"

FPS_x5 = 150 # cam fps * 5 
# FPS_x5 = 145 # cam fps * 5 


def move_cv2_window_right_of_tkinter(root, cv2_window_name): #cam 위치를 tkinter의 우상단에 위치
    root.update_idletasks()
    x = root.winfo_rootx() + root.winfo_width()
    y = root.winfo_rooty()
    cv2.moveWindow(cv2_window_name, x, y)

def export_labels_to_csv(filename):
    with open(filename, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Iterate through the rows and columns of frame_content
        for row in range(frame_content.grid_size()[1]):  # Rows
            row_data = []
            for column in range(frame_content.grid_size()[0]):  # Columns
                label = frame_content.grid_slaves(row=row, column=column)[0]  # Get the label widget
                text = label.cget('text')
                row_data.append(text)
            csv_writer.writerow(row_data)


def calculate_optical_flow(prev_frame, curr_frame): # optical flow

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 1, 15, 1, 3, 1.2, 0)
    return flow

def process_video(video_150):
    prev_frame = None
    sign_history = []
    saved_images = []
    count = 0
    for frame in video_150: # video.shape == (150,224,224)
        frame = cv2.resize(frame, (224, 224), cv2.INTER_AREA) #224로 바꾸어 video화
        if prev_frame is not None:
            optical_flow = calculate_optical_flow(prev_frame, frame)
            vertical_mean = np.mean(optical_flow[..., 1])

            current_sign = np.sign(vertical_mean)
            if len(sign_history) > 0 and current_sign != sign_history[-1]:
                if len(sign_history) >= 3:
                    saved_images.append(frame)
                    count += 0.5
                sign_history = [current_sign]
            else:
                sign_history.append(current_sign)
                
        prev_frame = frame


    if len(saved_images) > 0:
        saved_images = np.average(np.array(saved_images), axis=0)
        return saved_images, count

def thread_start():
    global analysis_now
    global video_count
    global video
    time.sleep(11)
    if video_count==0:
        del video[:FPS_x5] # 처음 5초는 제거
        print("처음 5초는 제거")
        video_count+=1
    while analysis_now: # true면 시작
        # Add new labels to the grid_frame 
        
        # print(video)
        global total_count
        global total_hand
        global total_depth
        global total_release

        if event.is_set():
            print("스레드 종료")
        if len(video)<=FPS_x5: # 5초 분량 만큼 쌓이기 전에 시작하면안됨.
            time.sleep(5)
            continue


        # print(len(video))
        
        # if len(video)>=145:
        critical_avg_image, count = process_video(video[:FPS_x5]) #
        critical_avg_image = cv2.convertScaleAbs(critical_avg_image)
        critical_avg_image = cv2.cvtColor(critical_avg_image, cv2.COLOR_BGR2RGB)
        depth, release, hand = start_estimation(critical_avg_image)

        total_count = np.append(total_count,count)
        total_hand = np.append(total_hand,hand)
        total_depth = np.append(total_depth,depth)
        total_release = np.append(total_release,release)
        # 여기서 프레임 처리된 내용 활용
        # ...
        # print(depth,release,hand,count)
        # 학습한 결과 출력
        add_label_to_grid(video_count+1,0,f'{video_count*5} ~ {video_count*5+5}s')
        add_label_to_grid(video_count+1,1,count)
        add_label_to_grid(video_count+1,2,hand)
        add_label_to_grid(video_count+1,3,f'{depth} mm')
        add_label_to_grid(video_count+1,4,release)

        # 경계선
        add_label_to_grid(video_count+2,0,'------------------')
        add_label_to_grid(video_count+2,1,'------------------')
        add_label_to_grid(video_count+2,2,'------------------')
        add_label_to_grid(video_count+2,3,'------------------')
        add_label_to_grid(video_count+2,4,'------------------')
        # 평균값
        add_label_to_grid(video_count+3,0,'Overall (average)')
        add_label_to_grid(video_count+3,1,np.round(np.mean(total_count),2), 8)
        add_label_to_grid(video_count+3,2,Counter(total_hand).most_common(1)[0][0], 8)
        add_label_to_grid(video_count+3,3,f'{np.round(np.mean(total_depth),2)} mm', 8)
        add_label_to_grid(video_count+3,4,Counter(total_release).most_common(1)[0][0], 8)

        frame_content.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))  
        # print(f"지우기전:{len(video)}")
        del video[:FPS_x5] # 추론한 뒤 제거 -> video_count 증가
        video_count+=1
        # print(f"지운 후:{len(video)}")


def finish_analysis_thread():
    global analysis_now
    browse_button.config(state=tk.DISABLED)
    start_button.config(state=tk.NORMAL)
    analysis_now=False
    export_labels_to_csv(f"{save_path}.csv")
    

def start_analysis_thread():
    global start_button
    global video
    global video_start_time
    global timer
    start_button.config(state=tk.DISABLED)
    browse_button.config(state=tk.NORMAL)
    # video = [] # start analysis 클릭시 비디오 변수에 새로 담기 시작.
    video_start_time = time.time() # cam 화면에 시간 출력해주기 위함.
    timer = 'on' # cam 화면에 시간 출력해주기 위함.
    processing_thread = Thread(target=thread_start)
    processing_thread.start()



def camera():
    global frame_idx
    global video
    global video_count
    global analysis_now # done 누르면 false
    global total_count
    global total_hand
    global total_depth
    global total_release
    global timer
    timer = 'off'
    total_count = np.array(())
    total_hand = np.array(())
    total_depth = np.array(())
    total_release = np.array(())
    # global first_start # 스타트 버튼 누르면 처음 시작
    analysis_now = True
    video = []
    out_video = []
    video_count = 0    
    # processing_thread = Thread(target=thread_start)
    # processing_thread.start()  
    # frame_idx = 0
    frame_idx = 0


    cap = cv2.VideoCapture(0)  # 카메라 캡처 객체 생성
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        exit()
    # new_width = 224
    # new_height = 224
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, new_width)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, new_height) # resize를 미리 해서 넘겨주기 위함.
    # print("비디오 저장 시작.")
    


    # video_start_time = time.time()
    start_time = time.time()
    while True:
        # start_time = time.time()
        ret, frame = cap.read()
        frame_with_text = frame.copy() # imshow와 저장을 구분하기 위해.
        frame_idx += 1
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break
        # 화면에 프레임 표시
        if timer == 'on':
            # frame_with_text = frame.copy()
            video.append(frame)
            out_video.append(frame)
            elapsed_time = int(time.time() - video_start_time)
            text = f"{elapsed_time} Second"
            
            # 화면에 프레임 표시
            cv2.putText(frame_with_text, text, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            # if len(out_video) % FPS_x5 == 0: # 150 프레임이 몇초마다 저장되는지 보기 위함.
            #     finish_time = time.time()
            #     print(f'time:{finish_time-start_time}')
            
        
        cv2.imshow("Camera Stream", frame_with_text)
        move_cv2_window_right_of_tkinter(root, "Camera Stream")
        
        # fps = cap.get(cv2.CAP_PROP_FPS)  # 현재 카메라의 프레임 속도(FPS) 가져오기
        # print(f"현재 프레임 속도: {fps:.2f} FPS")

        if cv2.waitKey(1) & 0xFF == ord('q') or analysis_now==False:
            event.set() # 스레드 종료
            # processing_thread.join()  # 프레임 처리 스레드 종료 대기
            break
        # finish_time = time.time()
        # print(f'time:{finish_time-start_time}')


    # 작업이 끝난 후 비디오 저장 및 리소스 해제
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format
    out = cv2.VideoWriter(f'{save_path}.mp4', fourcc, 30, (frame.shape[1], frame.shape[0]))

    # Loop through the frames in the 'video' list and save them to the video file
    for out_frame in out_video:
        out.write(out_frame)

    # Release the VideoWriter and close the file
    out.release()
    cap.release()
    cv2.destroyAllWindows()

def add_label_to_grid(row, column, text, idx=None):
    fontsize = 17 if idx == 8 else 14

    label = tk.Label(frame_content, text=text, font=('Arial', fontsize))
    label.grid(row=row, column=column, padx=5, pady=5, sticky='nsew')

    frame_content.grid_rowconfigure(row, weight=1)
    frame_content.grid_columnconfigure(column, weight=1)

# 라벨 폰트 조건 설정
def get_label_font(row):
    return ('Arial', 17) if row == 0 or row == 8 else ('Arial', 14)


labels_info = {
    (0, 0): 'Times',
    (0, 1): 'Num of CCs',
    (0, 2): 'Hand position',
    (0, 3): 'Maximum depth of CCs',
    (0, 4): 'complete release of CCs',
    (1, 0): '------------------',
    (1, 1): '------------------',
    (1, 2): '------------------',
    (1, 3): '------------------',
    (1, 4): '------------------'
}

root = TkinterDnD.Tk()
root.title("HQC Estimator")
root.geometry('1200x800')
root.resizable(True, True) 

#전역변수 선언
processing_thread2 = Thread(target=camera)
processing_thread2.start()

# Apply ttk theme
style = ttk.Style()
style.theme_use('clam')
style.configure('big.TButton', font=('Arial', 20))

button_frame = tk.Frame(root)
button_frame.pack(fill=tk.BOTH, pady=10)

browse_button = ttk.Button(button_frame, text='Finish Analysis', command=finish_analysis_thread, state=tk.DISABLED, style='big.TButton')
browse_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

start_button = ttk.Button(button_frame, text='Start Analysis', command=start_analysis_thread, style='big.TButton') 
start_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

canvas = tk.Canvas(root)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)

frame_content = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame_content, anchor='nw')

for (row, column), text in labels_info.items():
    label = tk.Label(frame_content, text=text, font=get_label_font(row))
    label.grid(row=row, column=column, padx=5, sticky='nsew')

frame_content.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

root.mainloop()

