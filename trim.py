import subprocess
import json
import math
from moviepy.editor import VideoFileClip, concatenate_videoclips

def seconds_to_hh_mm_ss(seconds):
    # Round down the float to an integer
    seconds = math.floor(float(seconds))
    
    # Calculate hours, minutes, and seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    # Format as hh:mm:ss
    return f"{hours:02}:{minutes:02}:{secs:02}"

# Preprocess rally data
with open("rallies.json") as f_in:
    rally_dict = json.load(f_in)

rally_ranges = [(int(k.split('-')[0]), int(k.split('-')[1])) for k in list(rally_dict.keys())[:-1]]

segment_files = []

# Extract video segments
for idx, (start_frame, end_frame) in enumerate(rally_ranges):
    start_time = start_frame / 30  # Assuming 30 FPS
    duration = (end_frame - start_frame) / 30

    segment_file = f'output_segment_{idx}.mp4'

    # Extract the specific segment using ffmpeg, including audio
    ffmpeg_command = [
        'ffmpeg', '-i', 'media/abbie.mp4', '-ss', seconds_to_hh_mm_ss(start_time),
        '-c', 'copy', '-t', seconds_to_hh_mm_ss(duration), segment_file
    ]
    
    try:
        # Run ffmpeg and check if it was successful
        subprocess.run(ffmpeg_command, check=True)
        # Append the segment to the list only if extraction was successful
        segment_files.append(VideoFileClip(segment_file))
    except subprocess.CalledProcessError as e:
        print(f"Error extracting segment {idx}: {e}")

# Initialize output files
moviepy_outfile = "final_output.mp4"  # Define your output file name
temp_audiofile = "temp_audio.m4a"  # Temporary audio file for concatenation
output_movie = "final_movie.mp4"  # Final output movie file
ffmpeg_log = "ffmpeg_log.txt"  # Log file for ffmpeg

# Concatenate segments and save the final video with audio
if segment_files:
    final_clip = concatenate_videoclips(segment_files)
    final_clip.write_videofile(moviepy_outfile, temp_audiofile=temp_audiofile, codec="libx264", remove_temp=False, audio_codec='aac')

    command = [
        'ffmpeg',
        '-y',  # Approve output file overwrite
        '-i', moviepy_outfile,
        '-i', temp_audiofile,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-shortest',
        output_movie
    ]

    with open(ffmpeg_log, 'w') as f:
        process = subprocess.Popen(command, stderr=f)
        process.wait()  # Wait for the ffmpeg process to finish

    # Close all video clips to release resources
    for clip in segment_files:
        clip.close()
else:
    print("No segments were extracted successfully.")
