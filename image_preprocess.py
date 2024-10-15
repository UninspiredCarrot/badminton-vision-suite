import json
import cv2
import numpy as np

# Map original points to warped coordinates based on the transformation matrix
def map_original_to_warped(original_point, matrix):
    original_point = np.array(original_point, dtype=np.float32).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(original_point, matrix)

# Handle mouse click events to select points
points = []
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(param, (x, y), 5, (0, 0, 255), -1)
        points.append([x, y])
        print(f"Point: ({x}, {y})")

# # Get the corner points from user clicks
# def get_corners(frame):
#     cv2.namedWindow('Image')
#     cv2.setMouseCallback('Image', click_event, frame)

#     while True:
#         cv2.imshow('Image', frame)
#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('q') and len(points) == 4:  # Ensure exactly 4 points are selected
#             break
#         elif key == ord('q'):
#             print("Please select exactly 4 points.")
#     cv2.destroyAllWindows()
#     return points

# Get a specific frame from the video
def get_frame(video_path, frame_number=100):
    cap = cv2.VideoCapture(video_path)
    for _ in range(frame_number):
        ret, frame = cap.read()
        if not ret:
            print("Unable to read frame or end of video reached.")
            cap.release()
            return None
    cap.release()
    return frame

# Main function to execute the workflow
def main(video_path="media/perfect.mp4", corners=[[261, 241], [1054, 240], [1294, 748], [6, 748]]):
    frame = get_frame(video_path)
    if frame is None:
        return

    
    
    # Warp the frame based on the selected corners
    warped_frame, matrix = warp(frame, corners)
    
    # Save the warped frame
    cv2.imwrite('media/warped_frame.png', warped_frame)
    return warped_frame, matrix

# Warp the frame using perspective transformation
def warp(frame, corners):
    if len(corners) != 4:
        print("Error: 4 points are required for warping.")
        return None

    frame_height, frame_width = frame.shape[1], frame.shape[0]
    destination_points = np.float32([[0, 0], [frame_width, 0], [frame_width, frame_height], [0, frame_height]])
    
    # Compute the perspective transform matrix
    matrix = cv2.getPerspectiveTransform(np.float32(corners), destination_points)
    
    # Warp the image
    warped_frame = cv2.warpPerspective(frame, matrix, (frame_width, frame_height))
    return warped_frame, matrix

# Execute main function when script is run
if __name__ == "__main__":
    main()
