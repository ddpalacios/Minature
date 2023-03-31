import pyaudio
import pygame
import numpy as np
import sys
import wave
import librosa.display
import librosa
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.interpolate import interp1d

# Set the audio parameters
pygame.init()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Pygame setup
WIDTH = 1600
HEIGHT = 1000
max_color_scale = 32767 * 255
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Live Audio Visualization")

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open the microphone for recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Recording...")


def gradient(normalized_value):
    import colorsys

    # Map the normalized RMS value to the hue component of the HSV color space
    hue = normalized_value

    saturation = 1.0
    value = 1.0

    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    color = (int(r * 255), int(g * 255), int(b * 255))
    return color


def calculate_rms(audio_data):
    abs_audio_data = np.abs(audio_data)
    max_value = np.max(abs_audio_data)

    if max_value == 0:
        return 0

    scaled_audio_data = abs_audio_data / max_value
    squared_scaled_audio_data = np.square(scaled_audio_data)
    rms = max_value * np.sqrt(np.mean(squared_scaled_audio_data))
    return rms


def normalize_audio(audio_data, target_rms):
    epsilon = 1e-8  # Small constant value to prevent division by zero
    current_rms = calculate_rms(audio_data)
    print("Raw RMS:", current_rms)
    normalization_factor = target_rms / (current_rms + epsilon)
    # print("Normalization factor:", normalization_factor)

    return audio_data * normalization_factor


def check_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()


def update_spectrogram(screen, audio_signals):
    audio_signals = audio_signals.astype(np.float32) / (2 ** 15 - 1)
    stft_matrix = librosa.stft(audio_signals, n_fft=window_size, hop_length=hop_size)
    magnitude_spectrogram = np.abs(stft_matrix)
    db_spectrogram = librosa.amplitude_to_db(magnitude_spectrogram, ref=np.max)

    # Create a matplotlib figure for the spectrogram
    fig = Figure(figsize=(WIDTH / 100, HEIGHT / 100), dpi=100)
    ax = fig.gca()
    img = librosa.display.specshow(db_spectrogram, sr=44100, hop_length=hop_size, x_axis='time', y_axis='log', ax=ax,
                                   cmap='gray_r')

    # Add a colorbar (legend)
    fig.colorbar(img, ax=ax, format="%+2.0f dB")

    # Render the figure to the Pygame surface
    canvas = FigureCanvas(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    # Create a Pygame surface from the raw data
    spectrogram_surface = pygame.image.fromstring(raw_data, (WIDTH, HEIGHT), "RGB")

    # Draw the spectrogram surface on the screen
    screen.blit(spectrogram_surface, (0, 0))
    pygame.display.flip()


def draw_waveform(audio_data, screen):
    rms_value = calculate_rms(audio_signals)
    normalized_rms_value = rms_value / (2 ** 15 - 1)
    # print(normalized_rms_value)
    color = gradient(normalized_rms_value)
    print(color)

    screen.fill((0, 0, 0))
    num_samples = len(audio_data)
    x_spacing = WIDTH / num_samples

    for i in range(1, num_samples):
        x1 = (i - 1) * x_spacing
        x2 = i * x_spacing
        y1 = HEIGHT // 2 - audio_data[i - 1] * HEIGHT // (2 * 2 ** 15)
        y2 = HEIGHT // 2 - audio_data[i] * HEIGHT // (2 * 2 ** 15)

        pygame.draw.line(screen, color, (x1, y1), (x2, y2), 1)

    pygame.display.flip()


# def draw_waveform(audio_data, screen):
#     audio_signals_converted = audio_data.astype(np.float32) / (2 ** 15 - 1)
#     stft_matrix = librosa.stft(audio_signals_converted, n_fft=window_size, hop_length=hop_size)
#
#     target_rms = 0.25 * (2 ** 15 - 1)
#     normalized_audio = normalize_audio(audio_data, target_rms)
#
#     screen.fill((0, 0, 0))
#     num_samples = len(audio_data)
#     x_spacing = WIDTH / num_samples
#
#     # Calculate the average color for each time slice of the STFT matrix
#     magnitude_spectrogram = np.abs(stft_matrix)
#     normalized_magnitude_spectrogram = magnitude_spectrogram / np.max(magnitude_spectrogram)
#     colors = [gradient(np.mean(normalized_magnitude_spectrogram[:, i])) for i in range(normalized_magnitude_spectrogram.shape[1])]
#
#     # Map the average color to the corresponding segment of the sound wave
#     for i in range(1, num_samples):
#         x1 = (i - 1) * x_spacing
#         x2 = i * x_spacing
#         y1 = HEIGHT // 2 - audio_data[i - 1] * HEIGHT // (2 * 2 ** 15)
#         y2 = HEIGHT // 2 - audio_data[i] * HEIGHT // (2 * 2 ** 15)
#
#         color_index = int(i * len(colors) / num_samples)
#         color = colors[color_index]
#         pygame.draw.line(screen, color, (x1, y1), (x2, y2), 1)
#
#     pygame.display.flip()

# Define a function to convert a float value to an RGB color
def float_to_color(value):
    value = min(max(value, 0.0), 1.0)
    red = value / 255
    green = 255 - (value / 255)
    blue = 0
    return (red, green, blue)


def get_emotion(audio_signal):
    return


while True:
    check_events()
    data = stream.read(CHUNK)
    audio_signals = np.frombuffer(data, dtype=np.int16)

    # STFT parameters
    window_size = 1024
    hop_size = 10
    print(audio_signals)

    draw_waveform(audio_signals, screen)

    # update_spectrogram(screen, audio_signals)

    # # Calculate STFT using librosa
    # print(stft_matrix.shape)
    #
    # # Calculate the magnitude spectrogram from the STFT matrix
    # magnitude_spectrogram = np.abs(stft_matrix)
    #
    # # Convert the magnitude spectrogram to decibels (dB)
    # db_spectrogram = librosa.amplitude_to_db(magnitude_spectrogram, ref=np.max)
    #
    # # Create a matplotlib figure for the spectrogram
    # fig = Figure(figsize=(WIDTH / 100, HEIGHT / 100), dpi=100)
    # ax = fig.gca()
    # img = librosa.display.specshow(db_spectrogram, sr=44100, hop_length=hop_size, x_axis='time', y_axis='log', ax=ax,
    #                                cmap='gray_r')
    #
    # # Add a colorbar (legend)
    # fig.colorbar(img, ax=ax, format="%+2.0f dB")
    #
    # # Render the figure to the Pygame surface
    # canvas = FigureCanvas(fig)
    # canvas.draw()
    # renderer = canvas.get_renderer()
    # raw_data = renderer.tostring_rgb()
    #
    # # Create a Pygame surface from the raw data
    # spectrogram_surface = pygame.image.fromstring(raw_data, (WIDTH, HEIGHT), "RGB")
    #
    # # Draw the spectrogram surface on the screen
    # screen.blit(spectrogram_surface, (0, 0))
    # pygame.display.flip()

    # emotion = get_emotion(audio_signals)
    # color = convert_emotion_to_color(emotion)
    # sampling_rate = 44_100
    # # Plot the spectrogram
    # plt.figure(figsize=(10, 4))
    # librosa.display.specshow(db_spectrogram, sr=sampling_rate, hop_length=hop_size, x_axis='time', y_axis='log')
    # plt.colorbar(format='%+2.0f dB')
    # plt.title('Spectrogram')
    # plt.show()

stream.stop_stream()
stream.close()
audio.terminate()
