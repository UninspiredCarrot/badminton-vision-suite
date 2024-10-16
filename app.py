from flask import Flask, send_file
import main

app = Flask(__name__)

@app.route("/", methods=['GET'])
def process():
    # Call the main function, which returns a figure object
    fig = main.main(
        video_path="media/perfectly-small.mp4", 
        minimum_movement=100, 
        bins=[60, 130], 
        alpha=0.6, 
        title="rally", 
        output_path="media/heatmap.png", 
        corners=[[261, 241], [1054, 240], [1294, 748], [6, 748]]
    )
    
    # Save the figure to a file
    output_path = "media/heatmap_output.png"
    fig.savefig(output_path)
    
    # Return the saved image file as a response
    return send_file(output_path, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
