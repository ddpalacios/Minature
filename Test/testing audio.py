from Soundscape import SoundscapeDatabase
import base64
import numpy as np
import math
import matplotlib.pyplot as plt
def draw_waveform(audio_data):
    CHUNK = 1024

    normalized_audio = normalize_audio(audio_data)

    num_samples = len(normalized_audio)
    x_spacing = 1.0 / num_samples

    x_values = np.linspace(0, 1, num_samples)
    y_values = np.zeros_like(x_values)

    for i in range(1, num_samples):
        segment_rms = calculate_rms(normalized_audio[max(0, i - CHUNK):min(num_samples, i + CHUNK)])
        normalized_rms_value = segment_rms / (2 ** 15 - 1)
        color = gradient(normalized_rms_value)

        x_values[i] = i * x_spacing
        y_values[i] = normalized_audio[i] / (2 ** 15)

        plt.plot(x_values[i - 1:i + 1], y_values[i - 1:i + 1], color=color)

    plt.show()


def calculate_rms(audio_data):
    abs_audio_data = np.abs(audio_data)
    max_value = np.max(abs_audio_data)

    if max_value == 0:
        return 0

    scaled_audio_data = abs_audio_data / max_value
    squared_scaled_audio_data = np.square(scaled_audio_data)
    rms = max_value * np.sqrt(np.mean(squared_scaled_audio_data))
    return rms


def normalize_audio(audio_data):
    target_rms = 0.25 * (2 ** 15 - 1)
    epsilon = 1e-8  # Small constant value to prevent division by zero
    current_rms = calculate_rms(audio_data)
    print("Raw RMS:", current_rms)
    normalization_factor = target_rms / (current_rms + epsilon)
    # print("Normalization factor:", normalization_factor)

    return audio_data * normalization_factor


db = SoundscapeDatabase()

# for audio in db.get_all_audio():
audio = db.get_all_audio()[0]
audio_blob = audio['audio_file']
decoded_bytes = base64.b64decode(audio_blob)

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
    print(chunk)
    # rms = np.sqrt(np.mean(chunk ** 2))
    # print(f"Chunk {i + 1} RMS: {rms}")
