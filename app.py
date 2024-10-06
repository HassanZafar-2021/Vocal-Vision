import os
import requests
import json
from pyannote.audio import Pipeline
from pydub import AudioSegment
import ffmpeg
from tempfile import NamedTemporaryFile
import time
from transformers import pipeline
import soundfile as sf
import pickle
from tqdm import tqdm
from moviepy.editor import *


HUGGING_FACE_TOKEN = "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"
GOOEY_API_KEY = "sk-HGaovVUDOJjviGvPxbFhYnexMnKQgJShGeg3qdbHJ7hwQ1bQ"

# Function to perform speaker diarization
def diarize_audio(audio_path):
    """
    Performs speaker diarization on the input audio file.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        diarization (Annotation): Diarization results.
    """
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HUGGING_FACE_TOKEN)
    diarization = pipeline(audio_path)
    return diarization


# Function to split and merge audio segments by speaker, including gaps between consecutive segments
def split_audio_by_speaker(audio_path, diarization):
    """
    Splits and merges the audio file into segments based on speaker diarization.
    Consecutive segments by the same speaker, including gaps, are combined.

    Args:
        audio_path (str): Path to the audio file.
        diarization (Annotation): Diarization results.

    Returns:
        speaker_segments (list): List of dictionaries containing speaker segments.
    """
    # Load the full audio file
    audio = AudioSegment.from_file(audio_path)
    speaker_segments = []

    current_speaker = None
    current_start = None
    current_end = None  # Track end time across multiple segments

    # Iterate over diarization results
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start_ms = int(turn.start * 1000)  # Convert start time to milliseconds
        end_ms = int(turn.end * 1000)      # Convert end time to milliseconds

        # If the current segment is by the same speaker as the previous one
        if speaker == current_speaker:
            # Just update the end time to extend the segment (includes gaps)
            current_end = end_ms
        else:
            # If the speaker changes, save the previous segment with the gap included
            if current_speaker is not None:
                speaker_segments.append({
                    'speaker': current_speaker,
                    'start': current_start,
                    'end': current_end,  # End time of the last segment for that speaker
                    'audio': audio[current_start:current_end]  # Include gaps in the audio
                })

            # Reset for the new speaker segment
            current_speaker = speaker
            current_start = start_ms  # Start time of the new speaker's first segment
            current_end = end_ms  # End time of the new speaker's first segment

    # Append the last speaker segment
    if current_speaker is not None:
        speaker_segments.append({
            'speaker': current_speaker,
            'start': current_start,
            'end': current_end,
            'audio': audio[current_start:current_end]
        })

    return speaker_segments


# Function to generate video using Gooey.AI API
def generate_video(segment, speaker_images):
    """
    Generates a lip-synced video using the Gooey.AI API.

    Args:
        segment_audio (AudioSegment): Audio segment of the speaker.
        image_path (str): Path to the speaker's image.
        api_key (str): Gooey.AI API key.

    Returns:
        video_filename (str): Filename of the downloaded video.
    """
    speaker = segment['speaker']
    segment_audio = segment['audio']
    start_time = segment['start']
    image_path = speaker_images.get(speaker)

    if not image_path:
        raise ValueError(f"No image found for speaker {speaker}")
    

    
    tmp_audio_file_name = f'tmp/tmp_audio_{speaker}.wav'
    segment_audio.export(tmp_audio_file_name, format='wav')

    files = [
        ("input_face", open(image_path, "rb")), 
        ("input_audio", open(tmp_audio_file_name, "rb")), 
    ]
    payload = {}

    response = requests.post(
        "https://api.gooey.ai/v2/Lipsync/form/?run_id=fecsii61rs6e&uid=fm165fOmucZlpa5YHupPBdcvDR02",
        headers={
            "Authorization": "Bearer " + GOOEY_API_KEY,
        },
        files=files,
        data={"json": json.dumps(payload)},
    )
    assert response.ok, response.content

    result = response.json()
    
    # Download the video
    video_response = requests.get(result['output']['output_video'])
    video_filename = f"vids_to_join/{speaker}_{start_time}.mp4"
    with open(video_filename, 'wb') as f:
        f.write(video_response.content)
        
    return video_filename


# Function to concatenate videos
def concatenate_videos(video_files, output_filename):
    """
    Concatenates a list of video files into a single video.

    Args:
        video_files (list): List of video filenames.
        output_filename (str): Filename for the concatenated video.
    """
    # Create input streams for ffmpeg
    input_streams = []
    for video_file in video_files:
        input_streams.append(ffmpeg.input(video_file))

    # Concatenate videos
    ffmpeg.concat(*input_streams, v=1, a=1).output(output_filename).run(overwrite_output=True)
    

def concatenate_videos(video_files, output_filename):
    """
    Concatenates a list of video files into a single video.

    Args:
        video_files (list): List of video filenames.
        output_filename (str): Filename for the concatenated video.
    """
    input_streams = []
    for video_file in video_files:
        input_streams.append(VideoFileClip(video_file))
        
    final = concatenate_videoclips(input_streams)
    final.write_videofile(f'final_vid/{output_filename}.mp4')
    
    

# Main function to tie everything together
def main():
    # Replace with your file paths and API key
    audio_path = 'notebook_podcast_1m.wav'
    male_image_path = 'images\Mark_Zuckerberg_720.jpg'
    female_image_path = 'images\Scarlett-Johansson_720.jpg '

    # Step 1: Speaker Diarization
    print("Performing speaker diarization...")
    diarization = diarize_audio(audio_path)

    # Step 2: Split Audio by Speaker
    print("Splitting audio by speaker...")
    speaker_segments = split_audio_by_speaker(audio_path, diarization)

    # Map speakers to images (Adjust the mapping as needed)
    speaker_images = {
        'SPEAKER_00': male_image_path,
        'SPEAKER_01': female_image_path,
    }

    # Step 3: Generate Videos for Each Segment
    print("Generating videos for each segment...")
    video_files = []
    for segment in tqdm(speaker_segments):
        video_file = generate_video(segment, speaker_images)
        video_files.append(video_file)

    # Step 4: Concatenate Videos
    print("Concatenating videos...")
    output_filename = 'final_video'
    concatenate_videos(video_files, output_filename)

    print(f"Final video saved as {output_filename}")


if __name__ == "__main__":
    main()
