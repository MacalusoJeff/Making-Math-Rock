import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import mido

cwd = os.getcwd()
model_path = os.path.join(cwd, "Data/Models/smallLSTM.h5")
model = keras.models.load_model(model_path)
print("Model loaded")
print(model.summary())

# Set the directory containing the MIDI files
midi_dir = os.path.join(cwd, "Data/MIDIs/")
midis = []
for filename in os.listdir(midi_dir):
    if filename.endswith(".mid") or filename.endswith(".midi"):
        midis.append(os.path.join(midi_dir, filename))

# Double checking that the ticks per beat are consistent before converting generated songs back to MIDI files
# This will also be used to specify the length of songs in seconds when generating songs
all_ticks_per_beat = []
for midi in midis:
    mid = mido.MidiFile(midi)
    all_ticks_per_beat.append(mid.ticks_per_beat)

assert len(set(all_ticks_per_beat)) == 1, "Different ticks per beat in MIDI files"
ticks_per_beat = all_ticks_per_beat[0]


def generate_song(
    seed: np.ndarray, model, ticks_per_beat: int, num_seconds=15
) -> np.ndarray:
    """
    TODO: Add a temperature parameter, etc.
    """
    song = seed
    seq_length = seed.shape[0]
    num_notes = num_seconds * ticks_per_beat
    for i in range(num_notes):
        probabilities = model.predict(song[-seq_length:].reshape(1, seq_length, 127))
        notes_played = np.random.binomial(n=1, p=probabilities)
        song = np.append(song, notes_played, axis=0)
    return song


# Loading in the array of notes to be able to use as a seed
processed_midi_array_filepath = os.path.join(cwd, "Data/processed_midis.npy")
midi_array = np.load(processed_midi_array_filepath, allow_pickle=True)
random_row = np.random.randint(0, len(midi_array))
seed = midi_array[random_row, :, :]

song = generate_song(
    seed=seed, model=model, ticks_per_beat=ticks_per_beat, num_seconds=15
)

# Saving the generated song
generated_song_path = os.path.join(
    cwd, "Data/Outputs/GeneratedSongs/generated_song.npy"
)
np.save(generated_song_path, song)
print("Generated song saved to", generated_song_path)
