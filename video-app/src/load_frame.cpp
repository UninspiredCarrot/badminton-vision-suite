#include <cstdlib>
#include <ctime>
#include <vector>

extern "C" {
    #include <libavcodec/avcodec.h>
    #include <libavformat/avformat.h>
    #include <libswscale/swsc`ale.h>
    #include <inttypes.h>
    #include <libavutil/imgutils.h>
}

bool load_random_frames(const char* filename, int* width_out, int* height_out, std::vector<unsigned char*>& data_out) {

    // Initialize libavformat and open the file
    printf("Opening video file: %s\n", filename);
    AVFormatContext* av_format_ctx = avformat_alloc_context();
    if (!av_format_ctx) {
        printf("Could not create AVFormatContext\n");
        return false;
    }

    if (avformat_open_input(&av_format_ctx, filename, NULL, NULL) != 0) {
        printf("Could not open video file: %s\n", filename);
        return false;
    }
    printf("Video file opened successfully!\n");

    // Find the first video stream
    int video_stream_index = -1;
    AVCodecParameters* av_codec_params;
    const AVCodec* av_codec;

    for (int i = 0; i < av_format_ctx->nb_streams; ++i) {
        auto stream = av_format_ctx->streams[i];
        av_codec_params = stream->codecpar;
        av_codec = avcodec_find_decoder(av_codec_params->codec_id);

        if (!av_codec) {
            printf("Could not find decoder for stream %d\n", i);
            continue;
        }

        if (av_codec_params->codec_type == AVMEDIA_TYPE_VIDEO) {
            video_stream_index = i;
            printf("Found video stream at index %d\n", video_stream_index);
            break;
        }
    }

    if (video_stream_index == -1) {
        printf("Could not find a valid video stream inside file\n");
        return false;
    }

    // Set up codec context for decoder
    AVCodecContext* av_codec_ctx = avcodec_alloc_context3(av_codec);
    if (!av_codec_ctx) {
        printf("Could not allocate AVCodecContext\n");
        return false;
    }

    if (avcodec_parameters_to_context(av_codec_ctx, av_codec_params) < 0) {
        printf("Could not initialize AVCodecContext\n");
        return false;
    }

    if (avcodec_open2(av_codec_ctx, av_codec, NULL) < 0) {
        printf("Could not open codec\n");
        return false;
    }

    AVFrame* av_frame = av_frame_alloc();
    if (!av_frame) {
        printf("Could not allocate AVFrame\n");
        return false;
    }

    AVPacket* av_packet = av_packet_alloc();
    if (!av_packet) {
        printf("Could not allocate AVPacket\n");
        return false;
    }

    // Calculate total frames and random indices
    int64_t total_duration = av_format_ctx->streams[video_stream_index]->duration;  // Total duration in stream time base
    AVRational time_base = av_format_ctx->streams[video_stream_index]->time_base;   // Time base of the stream
    int fps = av_q2d(av_format_ctx->streams[video_stream_index]->avg_frame_rate);   // Frame rate (frames per second)

    int64_t total_frames = total_duration * fps * av_q2d(time_base);  // Approx total number of frames
    printf("Total frames: %" PRId64 "\n", total_frames);

    std::vector<int64_t> random_frame_indices;
    srand(time(NULL));  // Seed for randomness
    for (int i = 0; i < 7; ++i) {
        int64_t random_index = rand() % total_frames;
        random_frame_indices.push_back(random_index);
        printf("Random frame index %d: %" PRId64 "\n", i + 1, random_index);
    }

    // Set up a scaling context to convert the frame to RGB
    struct SwsContext* sws_ctx = sws_getContext(
        av_codec_ctx->width, av_codec_ctx->height, av_codec_ctx->pix_fmt,    // Source format
        av_codec_ctx->width, av_codec_ctx->height, AV_PIX_FMT_RGB24,         // Destination format
        SWS_BILINEAR, NULL, NULL, NULL);

    if (!sws_ctx) {
        printf("Could not initialize the conversion context\n");
        return false;
    }

    // Loop over the random frame indices
    for (int64_t frame_idx : random_frame_indices) {

        // Seek to the specific frame
        int64_t seek_target = av_rescale_q(frame_idx, (AVRational){1, fps}, time_base);
        if (av_seek_frame(av_format_ctx, video_stream_index, seek_target, AVSEEK_FLAG_BACKWARD) < 0) {
            printf("Failed to seek to frame %" PRId64 "\n", frame_idx);
            continue;
        }

        avcodec_flush_buffers(av_codec_ctx);  // Clear the codec buffers

        // Read frames until the target frame is decoded
        int frame_found = 0;
        while (av_read_frame(av_format_ctx, av_packet) >= 0) {
            if (av_packet->stream_index != video_stream_index) {
                av_packet_unref(av_packet);
                continue;
            }

            int response = avcodec_send_packet(av_codec_ctx, av_packet);
            if (response < 0) {
                printf("Error sending packet for decoding\n");
                break;
            }

            response = avcodec_receive_frame(av_codec_ctx, av_frame);
            if (response == AVERROR(EAGAIN) || response == AVERROR_EOF) {
                av_packet_unref(av_packet);
                continue;
            } else if (response < 0) {
                printf("Error during decoding\n");
                break;
            }

            // Successfully decoded a frame
            printf("Decoded frame at index %" PRId64 "\n", frame_idx);

            // Allocate memory for the RGB data of this frame
            unsigned char* rgb_data = (unsigned char*)av_malloc(av_image_get_buffer_size(AV_PIX_FMT_RGB24, av_frame->width, av_frame->height, 1));
            if (!rgb_data) {
                printf("Could not allocate memory for RGB frame\n");
                return false;
            }

            // Set up arrays for image data
            uint8_t* dest[4] = { rgb_data };
            int dest_linesize[4];
            av_image_fill_arrays(dest, dest_linesize, rgb_data, AV_PIX_FMT_RGB24, av_frame->width, av_frame->height, 1);

            // Convert the frame to RGB
            sws_scale(sws_ctx, av_frame->data, av_frame->linesize, 0, av_frame->height, dest, dest_linesize);

            data_out.push_back(rgb_data);  // Store the frame data
            frame_found = 1;
            break;
        }

        av_packet_unref(av_packet);
        if (!frame_found) {
            printf("Failed to find frame at index %" PRId64 "\n", frame_idx);
        }
    }

    *width_out = av_frame->width;
    *height_out = av_frame->height;

    // Clean up
    sws_freeContext(sws_ctx);
    avformat_close_input(&av_format_ctx);
    av_frame_free(&av_frame);
    av_packet_free(&av_packet);
    avcodec_free_context(&av_codec_ctx);

    return true;
}
