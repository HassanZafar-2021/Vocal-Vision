import os
import requests
import json
from pyannote.audio import Pipeline
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from tqdm import tqdm
from moviepy.editor import concatenate_videoclips, VideoFileClip

app = Flask(__name__)

# MongoDB Atlas connection (replace with your connection string)
client = MongoClient("mongodb+srv://hassaanzafar3:divhacks@divhacks.fxivv.mongodb.net/?retryWrites=true&w=majority&appName=DivHacks")
db = client['DivHacks']  # Database name

# Your Hugging Face and Gooey API keys
HUGGING_FACE_TOKEN = "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"
GOOEY_API_KEY = "sk-HGaovVUDOJjviGvPxbFhYnexMnKQgJShGeg3qdbHJ7hwQ1bQ"

# Example route
@app.route('/')
def index():
    return render_template('prac.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    audio_file = request.files['audio_file']
    if audio_file:
        # Save the file temporarily
        audio_path = os.path.join('tmp', audio_file.filename)
        audio_file.save(audio_path)

        # Call your main processing function here
        try:
            main(audio_path)  # Modify main to accept the path of the audio file
            return redirect(url_for('index'))  # Redirect to index after processing
        except Exception as e:
            print(f"Error processing audio: {e}")
            return render_template('index.html', error="An error occurred during processing.")
    else:
        return render_template('index.html', error="No audio file uploaded.")

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
    audio = AudioSegment.from_file(audio_path)
    speaker_segments = []

    current_speaker = None
    current_start = None
    current_end = None  # Track end time across multiple segments

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start_ms = int(turn.start * 1000)  # Convert start time to milliseconds
        end_ms = int(turn.end * 1000)      # Convert end time to milliseconds

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
def generate_video(segment, speaker_images):
    """
    Generates a lip-synced video using the Gooey.AI API.
    Args:
        segment (dict): Audio segment of the speaker.
        speaker_images (dict): Speaker images mapped to their IDs.
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
    input_streams = []
    for video_file in video_files:
        input_streams.append(VideoFileClip(video_file))

    final = concatenate_videoclips(input_streams)
    final.write_videofile(f'final_vid/{output_filename}.mp4')

# Main function to tie everything together
def main(audio_path):
    male_image_path = 'images/Mark_Zuckerberg_720.jpg'
    female_image_path = 'images/Scarlett-Johansson_720.jpg'

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

    print(f"Final video saved as {output_filename}.mp4")

if __name__ == '__main__':
    app.run(debug=True)
