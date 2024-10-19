import json
import time
import cv2

video_path = '/Users/bolt/Downloads/pranavi_abbie/full_vid.mp4'
cap = cv2.VideoCapture(video_path)

playing = True
frame_rate = cap.get(cv2.CAP_PROP_FPS)
frame_jump = int(frame_rate * 2)
delay = int(1000/frame_rate)

current_frame = 0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

def set_video_frame(frame_number):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

def apply_red_filter(frame):
    # Create a filter to emphasize red channel
    red_filtered_frame = frame.copy()
    red_filtered_frame[:, :, 1] = 0  # Set green channel to 0
    red_filtered_frame[:, :, 0] = 0  # Set blue channel to 0
    return red_filtered_frame

player1_name = input("player 1 name: ")
player2_name = input("player 2 name: ")

sets = [[player1_name, player2_name], [0,0], [0,0], [0,0]]
cutting = False
points = []

def increment_score(sets, highlighted_row):
    for i, set in enumerate(sets[1:]):
        score = set[highlighted_row]
        other_score = set[(highlighted_row + 1) % 2]
        if (score >= 21 or other_score >= 21) and abs(score - other_score) >= 2:
            continue
        else:
            sets[i+1][highlighted_row] += 1
            return sets
    return sets

def decrement_score(sets, highlighted_row):
    for i, set in enumerate(sets[1:][::-1]):
        if set[highlighted_row] == 0:
            continue
        else:
            sets[3-i][highlighted_row] -= 1
            return sets
    return sets

highlighted_row = 0

def draw_table(frame, sets):
    for i, set in enumerate(sets):
        x_position = 50 + i * 150
        for j, score in enumerate(set):
            y_position = 50 + j * 50
            # Clear old score by drawing a filled rectangle
            cv2.rectangle(frame, (x_position - 20, y_position - 30), (x_position + 60, y_position + 10), (0, 0, 0), -1)
            colour = (0, 255, 0) if j == highlighted_row else (255, 255, 255)
            cv2.putText(frame, str(score), (x_position, y_position), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2, cv2.LINE_AA)


fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("cut.mp4", fourcc, frame_rate, (int(cap.get(3)), int(cap.get(4))))

while cap.isOpened():
    print(f"playing: {playing}")
    print(f"cutting: {cutting}")
    
    if playing:
        ret, frame = cap.read()
        current_frame += 1
    draw_table(frame, sets)

    cv2.imshow('Video', frame)
    
    if not ret:
        print("End of video reached")
        break

    if cutting:
        frame = apply_red_filter(frame)
    else:
        out.write(frame)

    if delay < 0:
        # Speed-up video when delay is negative
        skip_frames = max(1, abs(delay))  # Ensure at least 1 frame is skipped
        current_frame = min(current_frame + (frame_jump//2), total_frames - 1)
        set_video_frame(current_frame)
        key = cv2.waitKey(1) & 0xFF  # No delay, as you're skipping frames
    else:
        key = cv2.waitKey(delay) & 0xFF  # Normal delay behavior when delay >= 0


    if key == ord('p'):
        playing = not playing

    elif key == ord('r'):
        current_frame = max(current_frame - frame_jump, 0)
        set_video_frame(current_frame)
        playing = True

    elif key == ord('f'):
        current_frame = min(current_frame + frame_jump, total_frames - 1)
        set_video_frame(current_frame)
        playing = True
    
    elif key == ord('c'):
        delay+=5

    elif key == ord('v'):
        delay-=5
    
    elif key == ord('h'):
        highlighted_row = (highlighted_row+1)%2

    elif key == ord('w'):
        sets = increment_score(sets, highlighted_row)

    elif key == ord('s'):
        sets = decrement_score(sets, highlighted_row)

    elif key == ord('k'):
        points.append({
            "start": current_frame,
            "end": 0,
            "score": sets
        })
        cutting = True

    elif key == ord('l'):
        points[-1]['end'] = current_frame
        cutting = False
    
    
        

    elif key == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
print(points)
with open('points.json', 'w') as fp:
    json.dump(points, fp)