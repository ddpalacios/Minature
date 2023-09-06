import requests
import json
import pprint
import numpy as np
import base64
import certifi
import math
import urllib3
url = "https://life-of-sounds.herokuapp.com/audio_info/"
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where())
CHUNKS = 1024
response = requests.get(url)
response = response.json()
response = response['value'][0]
encoded_blob_file = response['value']['audio_blob']['audio_blob_file']

decoded_bytes = base64.b64decode(encoded_blob_file)
# Determine the element size (e.g., 2 bytes for int16)
element_size = np.dtype(np.int16).itemsize

# Calculate the padding size required to make the buffer size a multiple of the element size
padding_size = (element_size - (len(decoded_bytes) % element_size)) % element_size

# Pad the decoded bytes with zeros
decoded_bytes_padded = decoded_bytes + b'\x00' * padding_size

# Convert bytes to a NumPy array
audio_data = np.frombuffer(decoded_bytes_padded, dtype=np.int16)

# Set the chunk size
chunk_size = 1024  # Adjust this value as needed

# Calculate the number of chunks
num_chunks = int(math.ceil(len(audio_data) / chunk_size))

# Iterate through the chunks and calculate RMS for each chunk
for i in range(num_chunks):
    start = i * chunk_size
    end = min((i + 1) * chunk_size, len(audio_data))
    chunk = audio_data[start:end]
    rms = np.sqrt(np.mean(chunk ** 2))
    print(f"Chunk {i+1} RMS: {rms}")


