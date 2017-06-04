#!/usr/bin/env python3

import sys
import wave

if len(sys.argv) < 3:
    usage_string = "Usage: {} <input_file> <struct_name>\n"
    sys.stderr.write(usage_string.format(sys.argv[0]))
    sys.exit(1)

input_file = sys.argv[1]
struct_name = sys.argv[2]

wave_file = wave.open(input_file, "rb")

sampling_rate = wave_file.getframerate()
channels_number = wave_file.getnchannels()
frames_number = wave_file.getnframes()
sample_width = wave_file.getsampwidth()

sys.stdout.write("const int16_t {}_data[] = {{\n".format(struct_name))

bad_frames = 0

for frame in range(frames_number):
    frame_data = wave_file.readframes(1)
    if len(frame_data) != channels_number * sample_width:
        eof_string = "Frame {:d} of {:d} has size {:d} ({:d} expected)\n"
        sys.stderr.write(eof_string.format(frame,
                                           frames_number,
                                           len(frame_data),
                                           channels_number * sample_width))
        bad_frames += 1
        continue

    for channel in range(channels_number):
        if sample_width == 1:
            sample = (int(frame_data[channel]) - 128) << 8
        else:
            offset = (channel + 1) * sample_width
            raw_sample = int(frame_data[offset - 2])
            raw_sample += int(frame_data[offset - 1]) << 8
            sample = raw_sample
            if sample >= 0x8000:
                sample -= 2 ** 16

        if frame * channels_number + channel != 0:
            if (frame * channels_number + channel) % 8 == 0:
                sys.stdout.write(",\n    ")
            else:
                sys.stdout.write(", ")
        else:
            sys.stdout.write("    ")

        sys.stdout.write("{:d}".format(sample))

sys.stdout.write("};\n\n")

sys.stdout.write("const struct RawAudio_t {} = {{\n".format(struct_name))
sys.stdout.write("    {:d},\n".format(sampling_rate))
sys.stdout.write("    {:d},\n".format(channels_number))
sys.stdout.write("    {:d},\n".format(frames_number - bad_frames))
sys.stdout.write("    {}_data\n".format(struct_name))
sys.stdout.write("};\n\n")

wave_file.close()
