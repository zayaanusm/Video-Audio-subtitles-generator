from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import os
import assemblyai as aai

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'mp4', 'mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'  # Necessary for flash messages

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processvid(filepath):
    aai.settings.api_key = "#api key"
    with open(filepath, 'rb') as file:
        transcript = aai.Transcriber().transcribe(file.read())
    subtitles = transcript.export_subtitles_srt()
    
    # Ensure the static folder exists
    if not os.path.exists("static"):
        os.makedirs("static")
    
    # Save the subtitles in the static folder
    with open(os.path.join("static", "subtitles.srt"), "w") as f:
        f.write(subtitles)


@app.route('/') 
def hello_world():
    return render_template('video.html')

@app.route('/edit', methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        
        file = request.files['file']
        
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return "no selected files"
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            processvid(filepath)
            flash(f"Your subtitles can be viewed <a href='/static/subtitles.srt'>here</a>")
            return render_template("video.html")
    
    return render_template("video.html")

if __name__ == "__main__":
    app.run(debug=True)
