import base64
import numpy as np


class Audio:
    def __init__(self,
                 audio_name,
                 create_date,
                 encoded_audio_blob,
                 id,
                 audio_blob_id,
                 audio_type_id,
                 audio_subtype_id,
                 audio_type,
                 audio_subtype,
                 audio_image_url,
                 ):
        self.id = id
        self.audio_name = audio_name
        self.audio_subtype = audio_subtype
        self.create_date = create_date
        self.decoded_audio_blob = None
        self.encoded_audio_blob = encoded_audio_blob
        self.audio_data = None
        self.audio_blob_id = audio_blob_id
        self.audio_type = audio_type
        self.audio_type_id = audio_type_id
        self.audio_subtype_id = audio_subtype_id
        self.audio_image_url = audio_image_url
        self.convert_audio_data(self.encoded_audio_blob)

    def convert_audio_data(self, encoded_audio_blob_file):
        decoded_bytes = base64.b64decode(encoded_audio_blob_file)
        # Determine the element size (e.g., 2 bytes for int16)
        element_size = np.dtype(np.int16).itemsize
        # Calculate the padding size required to make the buffer size a multiple of the element size
        padding_size = (element_size - (len(decoded_bytes) % element_size)) % element_size
        # Pad the decoded bytes with zeros
        decoded_bytes_padded = decoded_bytes + b'\x00' * padding_size
        # Convert bytes to a NumPy array
        converted_audio_data = np.frombuffer(decoded_bytes_padded, dtype=np.int16)
        self.decoded_audio_blob = converted_audio_data
        return self.decoded_audio_blob

    def set_audio_data(self, audio_data):
        self.audio_data = audio_data

    def get_audio_data(self):
        return self.audio_data
