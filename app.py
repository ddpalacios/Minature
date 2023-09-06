from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, LargeBinary, BigInteger, inspect, Column, Integer, String, text
from flask_migrate import Migrate
import datetime

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
from flask_sqlalchemy import SQLAlchemy
import os
import base64
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
url = "postgresql://cmcdpjtcbuwchf:4a7ae0c24301ebd0947c1f25992950e9e63152273d1ed8c2543ea3e23fc9539f@ec2-35-169-9-79.compute-1.amazonaws.com:5432/d6p31v6dmrs0l6"

DATABASE_URL = os.environ.get('DATABASE_URL', url)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

db = SQLAlchemy(app)
engine = create_engine(DATABASE_URL)

connection = engine.connect()

Session = sessionmaker(bind=engine)
session = Session()

migrate = Migrate(app, db)

def execute_query(new_query):
    query = text(new_query)
    result = connection.execute(query)
    column_names = result.keys()
    records = []
    for record in result:
        audio_record = {}
        for value, col in zip(record, column_names):
            audio_record[col] = value
        records.append(audio_record)

    return records


class Audio_Info(db.Model):
    __tablename__ = 'Audio_Info'
    audio_blob_id = Column(Integer, nullable=False)
    audio_type_id = Column(Integer, nullable=False)
    audio_subtype_id = Column(Integer, nullable=True)
    audio_image_url = Column(LargeBinary, nullable=True)

    id = Column(Integer, primary_key=True)

    audio_create_date = Column(BigInteger, nullable=False)
    audio_name = Column(String(255), nullable=False)
    audio_type = Column(String(255), nullable=False)
    audio_subtype = Column(String(255), nullable=True)

    def __init__(self, id, audio_blob_id, audio_type_id, audio_subtype_id, create_date, audio_name, audio_type,
                 audio_subtype):
        self.audio_create_date = create_date
        self.audio_name = audio_name
        self.audio_type = audio_type
        self.audio_subtype = audio_subtype
        self.id = id
        self.audio_blob_id = audio_blob_id
        self.audio_type_id = audio_type_id
        self.audio_subtype_id = audio_subtype_id


class Audio_Blob(db.Model):
    __tablename__ = 'Audio_Blob'
    id = Column(Integer, primary_key=True)
    audio_info_id = Column(Integer, nullable=True)
    audio_size = Column(String(255), nullable=True)
    audio_blob_file = Column(LargeBinary, nullable=False)

    def __init__(self, audio_blob_file, id, audio_info_id):
        self.audio_blob_file = audio_blob_file
        self.id = id
        self.audio_info_id = audio_info_id


class Audio_Subtype(db.Model):
    __tablename__ = 'Audio_Subtype'
    id = Column(Integer, primary_key=True)
    audio_type_id = Column(Integer, nullable=False)
    audio_create_date = Column(String(80), nullable=False)
    audio_value = Column(String(80), nullable=False)
    key_signature = Column(String(50), nullable=False)

    def __init__(self, audio_create_date, audio_value, audio_type_id, key_signature=None):
        self.audio_create_date = audio_create_date
        self.audio_value = audio_value
        self.audio_type_id = audio_type_id
        self.key_signature = key_signature


class Audio_Type(db.Model):
    __tablename__ = 'Audio_Type'
    id = Column(Integer, primary_key=True)
    audio_create_date = Column(String(80), nullable=False)
    audio_value = Column(String(80), nullable=False)

    def __init__(self, audio_create_date, audio_value):
        self.audio_create_date = audio_create_date
        self.audio_value = audio_value


# @app.before_request
# def create_tables():
#     db.create_all()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/', methods=['POST', 'GET'])
def index():
    """Serve the index HTML"""
    return render_template('index.html')


@app.route('/audio_blob/<int:blob_id>', methods=['GET'])
def get_audio_blob(blob_id):
    session = Session()
    audio_blob = session.query(Audio_Blob).filter(Audio_Blob.id == blob_id).first()
    session.close()

    if audio_blob is None:
        return jsonify({'error': 'Audio info not found'}), 404

    # Encode the audio_blob_file as a base64 string
    base64_encoded_bytes = base64.b64encode(audio_blob.audio_blob_file)
    base64_encoded_string = base64_encoded_bytes.decode('utf-8')

    response = {
        'id': audio_blob.id,
        'audio_info_id': audio_blob.audio_info_id,
        'audio_size': audio_blob.audio_size,
        'audio_blob_file': base64_encoded_string  # Use the base64-encoded string here
    }

    return jsonify(response)


@app.route('/audio_info/<int:audio_id>', methods=['GET'])
def get_audio_info(audio_id):
    session = Session()
    audio_info = session.query(Audio_Info).filter(Audio_Info.id == audio_id).first()
    expand = request.args.get('expand')

    if audio_info is None:
        session.close()
        return jsonify({'error': 'Audio info not found'}), 404

    response = {
        'id': audio_info.id,
        'audio_blob_id': audio_info.audio_blob_id,
        'audio_type_id': audio_info.audio_type_id,
        'audio_subtype_id': audio_info.audio_subtype_id,
        'audio_create_date': audio_info.audio_create_date,
        'audio_name': audio_info.audio_name,
        'audio_type': audio_info.audio_type,
        'audio_subtype': audio_info.audio_subtype,
        'audio_image_url': audio_info.audio_image_url,
    }

    if expand == 'audio_blob':
        audio_blob = session.query(Audio_Blob).filter(Audio_Blob.id == audio_info.audio_blob_id).first()
        if audio_blob:
            base64_encoded_bytes = base64.b64encode(audio_blob.audio_blob_file)
            base64_encoded_string = base64_encoded_bytes.decode('utf-8')
            response['audio_blob'] = {
                'id': audio_blob.id,
                'audio_size': audio_blob.audio_size,
                'audio_blob_file': base64_encoded_string
            }

    session.close()
    return jsonify(response)


@app.route('/audio_info/', methods=['GET'])
def get_all_audio_info():
    session = Session()
    audio_subtype_filter = request.args.get('audio_subtype')
    expand = request.args.get('expand')
    if audio_subtype_filter:
        all_audio_info = session.query(Audio_Info).filter(Audio_Info.audio_subtype == audio_subtype_filter).all()
    else:
        all_audio_info = session.query(Audio_Info).all()

    max_id_audio_info = session.query(Audio_Info).order_by(Audio_Info.id.desc()).first()
    latest_audio_create_date = max_id_audio_info.audio_create_date
    unix = int(latest_audio_create_date)
    unix /= 1000
    latest_audio_create_date = datetime.datetime.fromtimestamp(round(unix)).strftime('%m/%d/%Y %I:%M %p')
    session.close()
    response = []
    for audio_info in all_audio_info:
        audio_info_dict = {
            'id': audio_info.id,
            'audio_blob_id': audio_info.audio_blob_id,
            'audio_type_id': audio_info.audio_type_id,
            'audio_subtype_id': audio_info.audio_subtype_id,
            'audio_create_date': audio_info.audio_create_date,
            'audio_name': audio_info.audio_name,
            'audio_type': audio_info.audio_type,
            'audio_subtype': audio_info.audio_subtype,
            'audio_image_url': audio_info.audio_image_url,
        }

        if expand == 'audio_blob':
            audio_blob = session.query(Audio_Blob).filter(Audio_Blob.id == audio_info.audio_blob_id).first()
            if audio_blob:
                base64_encoded_bytes = base64.b64encode(audio_blob.audio_blob_file)
                base64_encoded_string = base64_encoded_bytes.decode('utf-8')
                audio_info_dict['audio_blob'] = {
                    'id': audio_blob.id,
                    'audio_size': audio_blob.audio_size,
                    'audio_blob_file': base64_encoded_string
                }

        response.append(audio_info_dict)

    item = {'total_count': len(response),
            'last update': latest_audio_create_date,
            'value': response}

    return jsonify(item)


@app.route('/add_audio', methods=['POST'])
def add_audio():
    blob_file = request.files['file_path']
    file_name = request.form['file_name']
    create_date = request.form['create_date']
    category = request.form['category']

    unix = int(create_date)
    unix /= 1000

    query = text("SELECT COUNT(*) FROM \"Audio_Info\"")
    result = connection.execute(query)
    total_count = result.scalar()

    new_blob_record = Audio_Blob(audio_blob_file=blob_file.stream.read(), id=total_count + 1,
                                 audio_info_id=total_count + 1)
    db.session.add(new_blob_record)

    audio_type_record = execute_query("SELECT * FROM \"Audio_Type\" WHERE audio_value = 'flute'")
    audio_type_id = audio_type_record[0]['id']
    audio_type_value = audio_type_record[0]['audio_value']

    audio_subtype_record = execute_query(f"SELECT * FROM \"Audio_Subtype\" WHERE audio_value = '{category}'")
    audio_subtype_id = audio_subtype_record[0]['id']
    audio_subtype_value = audio_subtype_record[0]['audio_value']

    new_audio_info_record = Audio_Info(
        id=total_count + 1,
        create_date=create_date,
        audio_name=file_name,
        audio_blob_id=total_count + 1,
        audio_type_id=audio_type_id,
        audio_subtype_id=audio_subtype_id,
        audio_type=audio_type_value,
        audio_subtype=audio_subtype_value)

    db.session.add(new_audio_info_record)
    print("Committing Records...")
    db.session.commit()
    print("Done.")
    audio_create_date = datetime.datetime.fromtimestamp(round(unix)).strftime('%m/%d/%Y %I:%M %p')
    inspector = inspect(engine)
    print("New Audio was inserted at", audio_create_date)
    for name in inspector.get_table_names():
        if name == 'soundscape_database':
            continue
        query = text(f"SELECT COUNT(*) FROM \"{name}\"")
        result = connection.execute(query)
        count = result.scalar()
        print(f"Count of rows in {name}: {count}")
    print()

    db.session.close()
    return jsonify({"message": "Audio added successfully"})


if __name__ == '__main__':
    app.run(debug=True)
