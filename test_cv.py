import cv2
import time
from datetime import timedelta

cap = cv2.VideoCapture("media/abbie.mp4")

# Check if the video file was opened correctly
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

frame_number = 0
time_list = []
total_starttime = time.perf_counter()  # Start total timer

while frame_number < 1000:
    starttime = time.perf_counter()
    
    ret, frame = cap.read()
    if not ret:  # Check if frame reading was successful
        print("End of video or cannot read the frame.")
        break
    
    duration = timedelta(seconds=time.perf_counter() - starttime)
    print(f"Frame {frame_number}, Processing Time: {duration}")
    time_list.append(duration.total_seconds())  # Store the duration in seconds
    
    frame_number += 1

# Calculate the average processing time
average_duration = sum(time_list) / len(time_list) if time_list else 0
total_duration = timedelta(seconds=(time.perf_counter() - total_starttime))
print(f"Average frame processing time: {timedelta(seconds=average_duration)}")
print(f"Total time for {frame_number} frames: {total_duration}")

cap.release()
