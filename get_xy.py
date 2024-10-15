from collections import defaultdict
import cv2
from ultralytics import YOLO

model = YOLO("models/yolo11s-pose.pt")
track_history = defaultdict(lambda: [])
points = {}

#In the default YOLO11 pose model, there are 17 keypoints, each representing a different part of the human body. Here is the mapping of each index to its respective body joint:
#0: Nose 1: Left Eye 2: Right Eye 3: Left Ear 4: Right Ear 5: Left Shoulder 6: Right Shoulder 7: Left Elbow 8: Right Elbow 9: Left Wrist 10: Right Wrist 11: Left Hip 12: Right Hip 13: Left Knee 14: Right Knee 15: Left Ankle 16: Right Ankle
mapping = "nose left_eye right_eye left_ear right_ear left_shoulder right_shoulder left_elbow right_elbow left_wrist right_wrist left_hip right_hip left_knee right_knee left_ankle right_ankle"
mapping = mapping.split()

def main(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_index = 0
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            results = model.track(frame, conf=0.2, tracker="bytetrack.yaml", persist=True)
            if results[0].boxes.id == None:
                continue
            print(f'Processing frame: {frame_index} of {int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}')

            #A tensor containing the x, y coordinates of keypoints with shape (N, K, 2), where N is the number of detections and K is the number of keypoints per detection.
            keypoints = results[0].keypoints.xy

            for i, detection in enumerate(keypoints):
                points[f'{frame_index}_{i}'] = {}
                for j, map in enumerate(mapping):
                    points[f'{frame_index}_{i}'][map] = detection[j].tolist()
        else:
            break

        frame_index += 1

    # with open('points.json', 'w') as fp:
    #     json.dump(points, fp)
    cap.release()
    return points


if __name__ == "__main__":
    main()