import cv2
from matplotlib import pyplot as plt
import numpy as np
import image_preprocess
from matplotlib.colors import LogNorm
import get_xy
import matplotlib
matplotlib.use('Agg')

def main(video_path="media/perfectly-small.mp4", minimum_movement=100, bins=[60, 130], alpha=0.6, title="rally", output_path="media/heatmap.png", corners=[[261, 241], [1054, 240], [1294, 748], [6, 748]]):
    frame, matrix = image_preprocess.main(video_path, corners)
    frame_height, frame_width, _ = frame.shape
    
    points = get_xy.main(video_path)
    points_list = []
    print(f"got points: {points}")

    for k, frame_person in points.items():
        last_value = [frame_width//2, frame_height//2]
        for i, j in enumerate(['left_ankle', 'right_ankle']):
            value = frame_person[j]
            if abs(value[0] - last_value[i]) < minimum_movement:
                continue
            transformed_points = image_preprocess.map_original_to_warped(value, matrix)[0][0].tolist()
            if 0 < transformed_points[0] < frame_width and 0 < transformed_points[1] < frame_height:
                points_list.append(transformed_points)
            last_value[i] = value
    
    print("making histogram")
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    heatmap, xedges, yedges = np.histogram2d(
        [x[0] for x in points_list],  
        [x[1] for x in points_list], 
        bins=bins,  
        range=[[0, frame_width], [0, frame_height]] 
    )

    plt.imshow(frame, aspect='auto', origin="upper")
    plt.pcolormesh(xedges, yedges, heatmap.T, shading='auto', cmap='cool', alpha=alpha, norm=LogNorm())
    plt.title(title)
    plt.xlabel('Court Width (cm)')
    plt.ylabel('Court Length (cm)')
    plt.grid(True)
    plt.colorbar(label='Foot Position Count')

    # Instead of saving the plot, return the figure object
    fig = plt.gcf()  # Get the current figure
    return fig


if __name__ == "__main__":
    fig = main()
    fig.savefig("media/heatmap_output.png")  # Save the figure outside the function
    plt.close(fig)  # Close the figure after saving
