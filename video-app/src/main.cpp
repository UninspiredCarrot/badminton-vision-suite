#include <stdio.h>
#include <GLFW/glfw3.h>
#include <cstdlib>
#include <ctime>
#include <vector>

bool load_random_frames(const char* filename, int* width_out, int* height_out, std::vector<unsigned char*>& data_out);

int main(int argc, const char** argv) {
    GLFWwindow* window;

    if (!glfwInit()) {
        printf("Could not initialize GLFW\n");
        return 1;
    }

    window = glfwCreateWindow(640, 480, "fmd", NULL, NULL);
    if (!window) {
        printf("Could not open window\n");
        glfwTerminate();
        return 1;
    }

    glfwMakeContextCurrent(window);

    int frame_width, frame_height;
    std::vector<unsigned char*> frames_data;
    if (!load_random_frames("/Users/bolt/code/badminton-track/media/abbie.mp4", &frame_width, &frame_height, frames_data)) {
        printf("Could not load video frames\n");
        return 1;
    }

    GLuint tex_handles[7];
    glGenTextures(7, tex_handles);
    for (int i = 0; i < 7; i++) {
        glBindTexture(GL_TEXTURE_2D, tex_handles[i]);
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, frame_width, frame_height, 0, GL_RGB, GL_UNSIGNED_BYTE, frames_data[i]);
    }

    int current_frame = 0;

    while (!glfwWindowShouldClose(window)) {
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // Set up orthographic projection
        int window_width, window_height;
        glfwGetFramebufferSize(window, &window_width, &window_height);
        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        glOrtho(0, window_width, 0, window_height, -1, 1);
        glMatrixMode(GL_MODELVIEW);

        // Render the current frame
        glEnable(GL_TEXTURE_2D);
        glBindTexture(GL_TEXTURE_2D, tex_handles[current_frame]);
        glBegin(GL_QUADS);
            glTexCoord2d(0, 0); glVertex2i(0, 0);
            glTexCoord2d(1, 0); glVertex2i(frame_width, 0);
            glTexCoord2d(1, 1); glVertex2i(frame_width, frame_height);
            glTexCoord2d(0, 1); glVertex2i(0, frame_height);
        glEnd();
        glDisable(GL_TEXTURE_2D);

        glfwSwapBuffers(window);
        glfwWaitEvents();

        // Cycle through frames
        current_frame = (current_frame + 1) % 7; // Loop back to 0 after 6
    }

    // Free the frame data
    for (unsigned char* frame_data : frames_data) {
        free(frame_data);
    }

    glfwTerminate();
    return 0;
}
