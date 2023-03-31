from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
import librosa
def calculate_rms(audio_data):
    abs_audio_data = np.abs(audio_data)
    max_value = np.max(abs_audio_data)

    if max_value == 0:
        return 0

    scaled_audio_data = abs_audio_data / max_value
    squared_scaled_audio_data = np.square(scaled_audio_data)
    rms = max_value * np.sqrt(np.mean(squared_scaled_audio_data))
    return rms

import colorsys

def gradient(normalized_rms_value):
    hue = normalized_rms_value
    saturation = 1.0
    lightness = 0.5

    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
    color = (r, g, b)
    return color


def normalize_audio(audio_data):
    target_rms = 0.25 * (2 ** 15 - 1)
    epsilon = 1e-8  # Small constant value to prevent division by zero
    current_rms = calculate_rms(audio_data)
    print("Raw RMS:", current_rms)
    normalization_factor = target_rms / (current_rms + epsilon)
    # print("Normalization factor:", normalization_factor)

    return audio_data * normalization_factor


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

class Audio:
    def __init__(self, file_name):
        self.file_name = fr"C:\Users\DPalacios\OneDrive - Impact Networking\Documents\Sound Recordings\{file_name}"
        self.audio_data = self.open_file()['audio_data']
        self.audio_rate = self.open_file()['audio_rate']

    def open_file(self):
        rate, audio_data = wavfile.read(self.file_name)
        audio_data.astype(np.int16)
        audio_info = {"audio_rate": rate, "audio_data": audio_data}
        return audio_info

    def change_channel_dimension(self):
        if self.audio_data.ndim > 1:
            audio_signals = np.mean(self.audio_data, axis=1).astype(np.int16)
        else:
            audio_signals = self.open_file()['audio_data']  # self.audio_data.astype(np.int16)

        self.audio_data = audio_signals

    def get_total_channels(self):
        return self.audio_data.ndim

    def get_audio_data(self):
        return self.audio_data

    def get_rate(self):
        return self.audio_rate

    def get_file_path(self):
        return self.file_name


if __name__ == "__main__":
    # audio = Audio(file_name=file_name)
    # audio.change_channel_dimension()
    #
    # draw_waveform(audio.get_audio_data())
    file_name = "HELLO_RecordingExample.wav"
    file_path = fr"C:\Users\DPalacios\OneDrive - Impact Networking\Documents\Sound Recordings\{file_name}"
    audio_data, sr = librosa.load(file_path, sr=None, mono=True)

    draw_waveform(audio_data)

    # for i in range(2):
    #     print("Audio Rate: {}\nTotal Audio Channel(s) {}\nAudio Matrix: {}".format(audio.get_rate(),
    #                                                                                audio.get_total_channels(),
    #                                                                                audio.get_audio_data()))
    #
    #     print()
