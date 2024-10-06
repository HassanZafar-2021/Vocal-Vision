import os
import requests
import json
from pyannote.audio import Pipeline
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import time
from tqdm import tqdm
from moviepy.editor import *

HUGGING_FACE_TOKEN = "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"
GOOEY_API_KEY = "sk-HGaovVUDOJjviGvPxbFhYnexMnKQgJShGeg3qdbHJ7hwQ1bQ"

# Function to perform speaker diarization
def diarize_audio(audio_path):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HUGGING_FACE_TOKEN)
    diarization = pipeline(audio_path)
    return diarization

# Function to split and merge audio segments by speaker, including gaps between consecutive segments
def split_audio_by_speaker(audio_path, diarization):
    audio = AudioSegment.from_file(audio_path)
    speaker_segments = []

    current_speaker = None
    current_start = None
    current_end = None

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start_ms = int(turn.start * 1000)
        end_ms = int(turn.end * 1000)

        if speaker == current_speaker:
            current_end = end_ms
        else:
            if current_speaker is not None:
                speaker_segments.append({
                    'speaker': current_speaker,
                    'start': current_start,
                    'end': current_end,
                    'audio': audio[current_start:current_end]
                })

            current_speaker = speaker
            current_start = start_ms
            current_end = end_ms

    if current_speaker is not None:
        speaker_segments.append({
            'speaker': current_speaker,
            'start': current_start,
            'end': current_end,
            'audio': audio[current_start:current_end]
        })

    return speaker_segments

# Function to generate video using Gooey.AI API
def generate_video(segment, speaker_images, TMP_FOLDER, VIDS_TO_JOIN_FOLDER):
    speaker = segment['speaker']
    segment_audio = segment['audio']
    start_time = segment['start']
    image_path = speaker_images.get(speaker)

    if not image_path:
        raise ValueError(f"No image found for speaker {speaker}")

    tmp_audio_file_name = os.path.join(TMP_FOLDER, f'tmp_audio_{speaker}_{start_time}.wav')
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
    video_filename = os.path.join(VIDS_TO_JOIN_FOLDER, f"{speaker}_{start_time}.mp4")
    with open(video_filename, 'wb') as f:
        f.write(video_response.content)

    return video_filename

# Function to concatenate videos
def concatenate_videos(video_files, output_filename, FINAL_VIDEO_FOLDER):
    input_streams = []
    for video_file in video_files:
        input_streams.append(VideoFileClip(video_file))

    final = concatenate_videoclips(input_streams)
    final_output_path = os.path.join(FINAL_VIDEO_FOLDER, f'{output_filename}.mp4')
    final.write_videofile(final_output_path)

# Main function to tie everything together
def main(audio_path, male_image_path, female_image_path):
    # Create required folders if they don't exist
    TMP_FOLDER = 'tmp'
    VIDS_TO_JOIN_FOLDER = 'vids_to_join'
    FINAL_VIDEO_FOLDER = 'final_vid'

    os.makedirs(TMP_FOLDER, exist_ok=True)
    os.makedirs(VIDS_TO_JOIN_FOLDER, exist_ok=True)
    os.makedirs(FINAL_VIDEO_FOLDER, exist_ok=True)

    # Step 1: Speaker Diarization
    print("Performing speaker diarization...")
    diarization = diarize_audio(audio_path)

    # Step 2: Split Audio by Speaker
    print("Splitting audio by speaker...")
    speaker_segments = split_audio_by_speaker(audio_path, diarization)

    # Map speakers to images
    speaker_images = {
        'SPEAKER_00': male_image_path,
        'SPEAKER_01': female_image_path,
    }

    # Step 3: Generate Videos for Each Segment
    print("Generating videos for each segment...")
    video_files = []
    for segment in tqdm(speaker_segments):
        video_file = generate_video(segment, speaker_images, TMP_FOLDER, VIDS_TO_JOIN_FOLDER)
        video_files.append(video_file)

    # Step 4: Concatenate Videos
    print("Concatenating videos...")
    output_filename = 'final_video'
    concatenate_videos(video_files, output_filename, FINAL_VIDEO_FOLDER)

    print(f"Final video saved as {output_filename}.mp4")

    return f"{output_filename}.mp4"
