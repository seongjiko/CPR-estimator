import cv2
import numpy as np

def calculate_optical_flow(prev_frame, curr_frame):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 1, 15, 1, 3, 1.2, 0)
    return flow

def process_video(video_path,start_frame):
    cap = cv2.VideoCapture(video_path)
    prev_frame = None
    sign_history = []
    saved_images = []
    count = 0
    i = 0
    frame_idx = -1
    finish_frame = start_frame + 145
    while(cap.isOpened()):
        ret, frame = cap.read()
        frame_idx += 1

        if ret == False:
            break
        if frame_idx <= start_frame or frame_idx > finish_frame : #각 구간별 5초씩 탐지
            continue



        frame = cv2.resize(frame, (224, 224), cv2.INTER_AREA)

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
        i += 1

    cap.release()

    if len(saved_images) > 0:
        saved_images = np.average(np.array(saved_images), axis=0)
        return saved_images, count
