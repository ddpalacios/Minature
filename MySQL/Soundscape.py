import os
import sqlite3
import librosa


class SoundscapeDatabase:
    def __init__(self, db_name="Soundscape.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_flute_table()

    def create_flute_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Flute (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            audio_file BLOB,
            audio_category TEXT,
            audio_createDate TEXT
        )
        """)
        self.conn.commit()

    def drop_table(self, table_name):
        self.cursor.execute(f"DROP TABLE {table_name}")
        self.conn.commit()

    def insert_audio(self, blob_file, file_name, create_date, category):
        self.cursor.execute(
            "INSERT INTO Flute (audio_file, file_name, audio_category, audio_createDate) VALUES (?, ?, ?, ?)",
            (blob_file, file_name, category, create_date))
        self.conn.commit()
        self.close()

    def insert_audio_from_local(self, file_path, file_name, audio_category, audio_createDate):
        with open(file_path, "rb") as file:
            audio_data = file.read()
            self.cursor.execute(
                "INSERT INTO Flute (audio_file, file_name, audio_category, audio_createDate) VALUES (?, ?, ?, ?)",
                (audio_data, file_name, audio_category, audio_createDate))
            self.conn.commit()

    def update_audio(self, audio_id, new_file_path):
        with open(new_file_path, "rb") as file:
            new_audio_data = file.read()
            self.cursor.execute("UPDATE Flute SET audio_file = ? WHERE id = ?", (new_audio_data, audio_id))
            self.conn.commit()

    def delete_audio(self, audio_id):
        self.cursor.execute("DELETE FROM Flute WHERE id = ?", (audio_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()


class Audio:
    def __init__(self, file_name):
        self.__file_name = file_name
        self.__file_path = fr"C:\Users\DPalacios\OneDrive - Impact Networking\Documents\Sound Recordings\{file_name}"
        self._audio_data = self.open_file()['audio_wave_form']
        self._sampling_rate = self.open_file()['sampling_rate']

    def get_file_name(self):
        return self.__file_name

    def open_file(self):
        audio_wave_form, sampling_rate = librosa.load(self.__file_path)
        audio_info = {"sampling_rate": sampling_rate, "audio_wave_form": audio_wave_form}
        return audio_info

    def get_file_path(self):
        return self.__file_path

    def get_audio_data(self):
        return self._audio_data

    def get_rate(self):
        return self._sampling_rate


def get_audio_files_from_directory(file_code=None, get_all=False, get_one=None, target_file_name=None):
    audio_files = []
    AUDIO_PATH = r"C:\Users\DPalacios\OneDrive - Impact Networking\Documents\Sound Recordings"
    for file_name in os.listdir(AUDIO_PATH):
        if get_all or (file_code and file_code in file_name) or (get_one and file_name == target_file_name):
            audio_files.append(Audio(file_name))
            if get_one and file_name == target_file_name:
                break

    return audio_files


if __name__ == '__main__':
    import datetime
    db = SoundscapeDatabase()
    db.drop_table("Flute")
    db.create_flute_table()
    flute_audio_files = get_audio_files_from_directory(file_code="FLUTE")
    current_date = str(datetime.datetime.today())
    for flute_audio in flute_audio_files:
        category = None
        file_name = flute_audio.get_file_name().replace("FLUTE_", "").lower()
        if 'tg' in file_name or \
                'vo' in file_name or \
                'chrom' in file_name or \
                'major' in file_name or \
                'minor' in file_name or \
                'trill' in file_name:

            category = 'Scale Pattern'

        elif 'harmonics' in file_name or \
                'whistle' in file_name:

            category = 'Harmonics'

        else:
            category = 'Warm-Up'

        db.insert_audio_from_local(flute_audio.get_file_path(),
                                   file_name,
                                   category,
                                   current_date)
    db.close()
