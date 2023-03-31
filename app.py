from flask import Flask, request, jsonify, render_template

from MySQL.Soundscape import SoundscapeDatabase

"""
1. warm-up 

- starts with free play (warm-up)


2. fundamentals

- longtones - typically with a tuner or a drone (type of tuner by hearing)
	- loud and soft playing 
	- tapers (end of notes)
	types of longtones:
		- vibrato

- harmonics
- scale patterns



3. Repertoire

- Etude - practice for mastering skill
- Solos - Real Music Pieces


"""
from flask import g

app = Flask(__name__)


@app.before_request
def before_request():
    g.db = SoundscapeDatabase()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


import numpy as np


@app.route('/', methods=['POST', 'GET'])
def index():
    """Serve the index HTML"""
    return render_template('index.html')


@app.route('/add_audio', methods=['POST'])
def add_audio():
    blob_file = request.files['file_path']
    file_name = request.form['file_name']
    create_date = request.form['create_date']
    category = request.form['category']
    g.db.insert_audio(blob_file.stream.read(), file_name, create_date, category)
    return jsonify({"message": "Audio added successfully"})


@app.route('/update_audio/<int:audio_id>', methods=['PUT'])
def update_audio(audio_id):
    new_file_path = request.form['new_file_path']
    g.db.update_audio(audio_id, new_file_path)
    return jsonify({"message": "Audio updated successfully"})


@app.route('/delete_audio/<int:audio_id>', methods=['DELETE'])
def delete_audio(audio_id):
    g.db.delete_audio(audio_id)
    return jsonify({"message": "Audio deleted successfully"})


if __name__ == '__main__':
    app.run(debug=True)
