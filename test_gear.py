import av
import time
from datetime import timedelta

# Open the video file using PyAV
container = av.open("media/abbie.mp4")

frame_number = 0
time_list = []

# Start total timer
total_starttime = time.perf_counter()

# Loop through video frames
for frame in container.decode(video=0):
    if frame_number >= 1000:
        break

    starttime = time.perf_counter()

    # Perform any processing you want on the frame here
    # For now, we are simply converting the frame to an image (which is optional)
    img = frame.to_image()

    # Measure time taken to process the frame
    duration = timedelta(seconds=time.perf_counter() - starttime)
    print(f"Frame {frame_number}, Processing Time: {duration}")
    time_list.append(duration.total_seconds())  # Store the duration in seconds
    
    frame_number += 1

# Calculate the average processing time
average_duration = sum(time_list) / len(time_list) if time_list else 0
total_duration = timedelta(seconds=(time.perf_counter() - total_starttime))

print(f"Average frame processing time: {timedelta(seconds=average_duration)}")
print(f"Total time for {frame_number} frames: {total_duration}")
