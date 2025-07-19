#!/bin/bash
# fade the last 5 seconds of audio in a video track, and write to output_faded.mp4
#
# By default, reads the file 'output_with_audio.mp4' but can be specified
#  by providing a filename
# writes to 'output_faded.mp4'
#
#
# EXAMPLE
#
#   slideshow-fade-audio.sh
#
#   slideshow-fade-audion.sh video_file.mp4
#
# REQUIREMENTS
# requires ffmpeg and bc

# Check if the input file path is provided as a command line argument
if [ -n "$1" ]; then
    input_file="$1"
else
    input_file="output_with_audio.mp4"
fi

# Specify the output video file path
output_file="output_faded.mp4"

# Set the fade duration in seconds
fade_duration=5

# Extract the audio from the input video
ffmpeg -i "$input_file" -vn -acodec copy audio.aac

# Get the audio duration
audio_duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 audio.aac)

# Calculate the start time for the fade effect
fade_start=$(bc <<< "$audio_duration - $fade_duration")

# Apply the fade effect to the audio
ffmpeg -i audio.aac -af "afade=t=out:st=$fade_start:d=$fade_duration" faded_audio.aac

# Replace the original audio in the video with the faded audio
ffmpeg -i "$input_file" -i faded_audio.aac -c:v copy -map 0:v:0 -map 1:a:0 "$output_file"

# Clean up temporary files
rm audio.aac faded_audio.aac

echo "Fade effect applied successfully to $input_file. Output file: $output_file"
