from flask import Flask, render_template, request, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename

# Import your backend functions
from backend import main  # Ensure your backend code is in backend.py

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER_AUDIO = 'uploads/audio'
UPLOAD_FOLDER_IMAGES = 'uploads/images'
FINAL_VIDEO_FOLDER = 'final_vid'
TMP_FOLDER = 'tmp'
VIDS_TO_JOIN_FOLDER = 'vids_to_join'

# Create required folders if they don't exist
os.makedirs(UPLOAD_FOLDER_AUDIO, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_IMAGES, exist_ok=True)
os.makedirs(FINAL_VIDEO_FOLDER, exist_ok=True)
os.makedirs(TMP_FOLDER, exist_ok=True)
os.makedirs(VIDS_TO_JOIN_FOLDER, exist_ok=True)

# Allowed extensions
ALLOWED_EXTENSIONS_AUDIO = {'wav', 'mp3', 'm4a'}
ALLOWED_EXTENSIONS_IMAGES = {'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER_AUDIO'] = UPLOAD_FOLDER_AUDIO
app.config['UPLOAD_FOLDER_IMAGES'] = UPLOAD_FOLDER_IMAGES
app.config['FINAL_VIDEO_FOLDER'] = FINAL_VIDEO_FOLDER
app.config['TMP_FOLDER'] = TMP_FOLDER
app.config['VIDS_TO_JOIN_FOLDER'] = VIDS_TO_JOIN_FOLDER

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/', methods=['GET', 'POST'])
def index():
    video_url = None
    if request.method == 'POST':
        # Check if files are present in the request
        if 'audioUpload' not in request.files or \
           'maleAvatar' not in request.files or \
           'femaleAvatar' not in request.files:
            return "Missing files", 400

        audio_file = request.files['audioUpload']
        male_avatar = request.files['maleAvatar']
        female_avatar = request.files['femaleAvatar']

        # Validate and save the uploaded files
        if audio_file and allowed_file(audio_file.filename, ALLOWED_EXTENSIONS_AUDIO):
            audio_filename = secure_filename(audio_file.filename)
            audio_path = os.path.join(app.config['UPLOAD_FOLDER_AUDIO'], audio_filename)
            audio_file.save(audio_path)
        else:
            return "Invalid audio file", 400

        if male_avatar and allowed_file(male_avatar.filename, ALLOWED_EXTENSIONS_IMAGES):
            male_avatar_filename = secure_filename(male_avatar.filename)
            male_avatar_path = os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], male_avatar_filename)
            male_avatar.save(male_avatar_path)
        else:
            return "Invalid male avatar image", 400

        if female_avatar and allowed_file(female_avatar.filename, ALLOWED_EXTENSIONS_IMAGES):
            female_avatar_filename = secure_filename(female_avatar.filename)
            female_avatar_path = os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], female_avatar_filename)
            female_avatar.save(female_avatar_path)
        else:
            return "Invalid female avatar image", 400

        # Run the backend processing code
        output_filename = main(audio_path, male_avatar_path, female_avatar_path)

        # Generate video URL for display
        video_url = url_for('final_video', filename=output_filename)

    return render_template('index.html', video_url=video_url)

# Route to serve the final video
@app.route('/final_vid/<filename>')
def final_video(filename):
    return send_from_directory(app.config['FINAL_VIDEO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
