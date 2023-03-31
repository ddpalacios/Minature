import librosa
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.colors import LinearSegmentedColormap

# def calculate_rms(signal):
#     return np.sqrt(np.mean(np.square(signal)))
#
#
# def get_audio_example(file_name):
#     return librosa.example(file_name)
#
#
# def get_audio_from_local(file_name):
#     return fr"C:\Users\DPalacios\OneDrive - Impact Networking\Documents\Sound Recordings\{file_name}.wav"


AUDIO_PATH = r"C:\Users\DPalacios\OneDrive - Impact Networking\Documents\Sound Recordings"


class Audio:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file_path = fr"C:\Users\DPalacios\OneDrive - Impact Networking\Documents\Sound Recordings\{file_name}"
        self._audio_data = self.open_file()['audio_wave_form']
        self._sampling_rate = self.open_file()['sampling_rate']

    def get_file_name(self):
        return self.file_name

    def open_file(self):
        audio_wave_form, sampling_rate = librosa.load(self.file_path)
        audio_info = {"sampling_rate": sampling_rate, "audio_wave_form": audio_wave_form}
        return audio_info

    def get_audio_data(self):
        return self._audio_data

    def get_rate(self):
        return self._sampling_rate


def close_plot(event):
    if event.key == 'q':
        plt.close()


def plot_audio(audio_files, num_columns=1):
    total_files = len(audio_files)
    num_rows = (total_files + num_columns - 1) // num_columns
    fig, axs = plt.subplots(num_rows, num_columns, figsize=(20 * num_columns, 20 * num_rows))
    axs = axs.flatten()

    # Create a custom white-to-blue color map
    colors = ["black" ,"pink"]
    cmap = LinearSegmentedColormap.from_list("white_to_blue", colors)
    # Set the axes background color to black
    for ax in axs:
        ax.set_facecolor('black')

    for i, audio_file in enumerate(audio_files):
        audio_wave_form, sampling_rate = audio_file.get_audio_data(), audio_file.get_rate()
        spec = librosa.feature.melspectrogram(y=audio_wave_form, sr=sampling_rate)
        db_spec = librosa.power_to_db(spec, ref=np.max)

        ax = axs[i]

        librosa.display.specshow(db_spec, y_axis='mel', x_axis='s', sr=sampling_rate, ax=ax, cmap=cmap)
        ax.set_title(audio_file.file_name)
        fig.colorbar(ax.collections[0], ax=ax, format="%+2.0f dB")

    # Remove unused subplots if any
    for i in range(len(audio_files), num_columns * num_rows):
        axs[i].axis('off')

    # remove the x and y ticks
    for ax in axs:
        ax.set_xticks([])
        ax.set_yticks([])

    # plt.tight_layout()
    # Increase spacing between subplots
    plt.subplots_adjust(hspace=0.6, wspace=.4)

    # get the current figure manager
    # manager = plt.get_current_fig_manager()
    #
    # # toggle full screen mode
    # manager.full_screen_toggle()

    plt.show()

    # connect the key press event to the custom function
    plt.connect('key_press_event', close_plot)

    # wait for the plot window to be closed
    plt.waitforbuttonpress()

    # close the plot window if it hasn't been closed already
    plt.close()


def get_audio_files(file_code=None, get_all=False, get_one=None, target_file_name=None):
    audio_files = []
    for file_name in os.listdir(AUDIO_PATH):
        if get_all or (file_code and file_code in file_name) or (get_one and file_name == target_file_name):
            audio_files.append(Audio(file_name))

            if get_one and file_name == target_file_name:
                break

    return audio_files



if __name__ == '__main__':
    audio_files = get_audio_files(file_code="FLUTE")
    plot_audio(audio_files, num_columns=5)

    # filename = get_audio_from_local(file_name='HERTZ_Crazy')
    # filename2 = get_audio_from_local(file_name='PROD_DevilsTrill')
    #
    # # Load the audio as a waveform `y`
    # #  Store the sampling rate as `sr`
    # audio_wave_form, sampling_rate = librosa.load(filename)
    # audio_wave_form2, sampling_rate2 = librosa.load(filename2)
    #
    # spec1 = librosa.feature.melspectrogram(y=audio_wave_form, sr=sampling_rate)
    # spec2 = librosa.feature.melspectrogram(y=audio_wave_form2, sr=sampling_rate2)
    #
    # print(sampling_rate)
    # print(audio_wave_form.shape, sampling_rate)
    # # iterate through sound wave in CHUNKS
    # CHUNKS = 1024
    # HOP_SIZE = 512
    #
    # """
    # Audio signal:       [---|---|---|---|---|---|---|---|---|---]
    # Window size (W):    [---|---|---]
    # Hop size (H):                   2
    #
    # Step 1:             [---|---|---]
    # Step 2:                         [---|---|---]
    # Step 3:                                     [---|---|---]
    #
    # num_windows:        (1     2     3) + 1
    #
    #
    # """
    #
    # # Convert to decibels
    # db_spec1 = librosa.power_to_db(spec1, ref=np.max)
    # db_spec2 = librosa.power_to_db(spec2, ref=np.max)
    #
    # # Create subplots
    # fig, axs = plt.subplots(2, 1, figsize=(10, 10))
    #
    # # Display first spectrogram
    # librosa.display.specshow(db_spec1, y_axis='mel', x_axis='s', sr=sampling_rate, ax=axs[0])
    # axs[0].set_title('Spectrogram for audio_file_1')
    # fig.colorbar(axs[0].collections[0], ax=axs[0], format="%+2.0f dB")
    #
    # # Display second spectrogram
    # librosa.display.specshow(db_spec2, y_axis='mel', x_axis='s', sr=sampling_rate2, ax=axs[1])
    # axs[1].set_title('Spectrogram for audio_file_2')
    # fig.colorbar(axs[1].collections[0], ax=axs[1], format="%+2.0f dB")
    #
    # plt.tight_layout()
    # plt.show()

    #
    # db_spec = librosa.power_to_db(spec, ref=np.max, )
    # librosa.display.specshow(db_spec, y_axis='mel', x_axis='s', sr=sampling_rate)
    # plt.colorbar()
    # plt.show()

    # total_amplitude_records = audio_wave_form.shape[0]
    # total_number_of_windows = total_amplitude_records - CHUNKS // HOP_SIZE + 1
    # rms_values = []
    # for window in range(total_number_of_windows):
    #     start_index = window * HOP_SIZE # 0 => 1024 (total chunk of amplitude values)
    #     end_index = start_index + CHUNKS
    #
    #     chunk_of_amplitude_values = audio_wave_form[start_index:end_index]
    #     if len(chunk_of_amplitude_values) > 0:
    #         # print(chunk_of_amplitude_values)
    #         print(calculate_rms(chunk_of_amplitude_values))
