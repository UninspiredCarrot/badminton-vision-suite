#include <libavutil/imgutils.h>
#include <libavformat/avformat.h>
#include <libavutil/avutil.h>
#include <stdio.h>

void print_avframe_info(AVFrame *frame) {
    if (!frame) {
        printf("Frame is null\n");
        return;
    }

    // Print basic information
    printf("Width: %d\n", frame->width);
    printf("Height: %d\n", frame->height);
    printf("Format: %d\n", frame->format); // AVPixelFormat
    printf("Linesize[0]: %d\n", frame->linesize[0]); // Y plane line size

    // Print pixel data for each plane
    for (int i = 0; i < 8; i++) { // Loop over the maximum number of planes
        if (i < AV_NUM_DATA_POINTERS) {
            printf("Data[%d]: %p\n", i, frame->data[i]);

            // Inspect the first few bytes of the pixel data
            for (int j = 0; j < 16; j++) { // Print first 16 bytes for inspection
                printf("%02x ", frame->data[i][j]);
            }
            printf("\n");
        }
    }
}

int main() {
    // Assume 'frame' is an already initialized AVFrame
    AVFrame *frame = ...; // Your AVFrame initialization logic

    // Print the frame information
    print_avframe_info(frame);

    return 0;
}
