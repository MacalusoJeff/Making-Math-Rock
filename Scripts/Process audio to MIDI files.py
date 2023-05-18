import os
import numpy as np
import tensorflow as tf
from basic_pitch import (
    inference as basic_pitch_inference,
)  # Spotify's library for converting mp3 to MIDI
from basic_pitch import (
    ICASSP_2022_MODEL_PATH,
)  # Recommended to load when predicting for multiple songs

cwd = os.getcwd()
mp3_directory = os.path.join(cwd, "Data/Songs/")
midi_directory = os.path.join(cwd, "Data/MIDIs/")

# Renaming all mp3s to numbers
mp3_index = 0
for root, dirs, files in os.walk(mp3_directory):
    for file in files:
        filepath = root + "\\" + file
        if filepath.lower().endswith(".mp3"):
            new_filepath = root + "\\" + str(mp3_index) + ".mp3"
            mp3_index += 1
            os.rename(filepath, new_filepath)

# Getting a list of already converted MIDI files and mp3s that need to be converted
mp3s = []
midis = []
for root, dirs, files in os.walk(midi_directory):
    for file in files:
        filepath = root + "\\" + file
        if filepath.lower().endswith(".mid"):
            midis.append(filepath)
for root, dirs, files in os.walk(mp3_directory):
    for file in files:
        filepath = root + "\\" + file
        if filepath.lower().endswith(".mp3"):
            mp3s.append(filepath)
mp3s = [
    mp3
    for mp3 in mp3s
    if mp3.replace(".mp3", ".mid").replace("/Songs/", "/MIDIs/") not in midis
]

# Iterating through the mp3s, converting them to MIDI, and saving them to the MIDI directory
basic_pitch_model = tf.saved_model.load(str(ICASSP_2022_MODEL_PATH))
log_file = open("Data/Outputs/processFailures.log", "w")  # To report issues
num_processed_songs = 0
for i, mp3 in enumerate(mp3s):
    print(f"{i / len(mp3s):.0%}")
    mp3_to_convert = mp3s[i]
    mp3 = mp3.replace("\\", "/")
    try:
        _, midi_data, _ = basic_pitch_inference.predict(mp3, basic_pitch_model)
        midi_path = mp3.replace("/Songs/", "/MIDIs/").replace(".mp3", ".mid")
        midi_data.write(midi_path)
        num_processed_songs += 1
    except Exception as e:
        print(f"Issue with {mp3}")
        log_file.write(f"{mp3}: {str(e)}\n")
        pass
log_file.close()

# Reporting the results
num_processed_songs = num_processed_songs
num_total_songs = len(mp3s)
print(
    f"Successfully processed {num_processed_songs}  \
      songs of {num_total_songs} ({(num_processed_songs / num_total_songs)})"
)
