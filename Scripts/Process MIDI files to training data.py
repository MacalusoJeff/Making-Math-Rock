import os
import numpy as np
import mido

# Get the list of the MIDI files
cwd = os.getcwd()
midi_directory = os.path.join(cwd, "Data\\MIDIs")
midis = []
for root, dirs, files in os.walk(midi_directory):
    for file in files:
        filepath = root + "\\" + file
        if filepath.lower().endswith(".mid"):
            midis.append(filepath)

# Double check that the ticks per beat are consistent in all of the MIDI files
# This will be used to specify the length in seconds to slice by
all_ticks_per_beat = []
for midi in midis:
    mid = mido.MidiFile(midi)
    all_ticks_per_beat.append(mid.ticks_per_beat)

assert len(set(all_ticks_per_beat)) == 1, "Different ticks per beat in MIDI files"
ticks_per_beat = all_ticks_per_beat[0]


def parse_midi_to_array(file_path: str) -> np.ndarray:
    """
    Parses a MIDI file and converts it into a NumPy array representing the song.

    Args:
        file_path (str): The path to the MIDI file.

    Returns:
        np.ndarray: A NumPy array representing the song.
            The X-axis represents the timestamp, and the Y-axis represents the pitch.

    Raises:
        FileNotFoundError: If the specified file_path does not exist.
    """
    # Load MIDI file
    mid = mido.MidiFile(file_path)

    # Initialize the song array with zeros
    # The X axis is the timestamp, and the Y axis is the pitch
    ticks_per_beat = mid.ticks_per_beat
    max_time = int(mid.length * ticks_per_beat)
    max_pitch = 127
    song_array = np.zeros((max_time, max_pitch), dtype=np.int8)

    # Create array of note on/off events
    note_events = []
    for msg in mid:
        if msg.type == "note_on":
            note_events.append((msg.note, msg.time))
        elif msg.type == "note_off":
            note_events.append((msg.note, msg.time))

    # Create array of note times
    note_times = []
    time = 0
    for event in note_events:
        note_times.append((event[0], time, event[1]))
        time += event[1]

    # Create array of note durations
    note_durations = []
    for i in range(len(note_times)):
        note = note_times[i]
        if i == len(note_times) - 1:
            duration = mid.length - note[1]
        else:
            duration = note_times[i + 1][1] - note[1]
        note_durations.append(duration)

    # Populate the song array
    for i in range(len(note_times)):
        note = note_times[i]
        duration = note_durations[i]
        start_time = int(note[1] * ticks_per_beat)
        end_time = int((note[1] + duration) * ticks_per_beat)
        pitch = note[0]
        song_array[start_time:end_time, pitch] = 1

    return song_array


# Converting the MIDI files to numpy arrays
# Saving the individual song arrays and creating one array of song arrays
midi_arrays = []
for midi in midis:
    parsed_midi = parse_midi_to_array(midi)
    midi_arrays.append(parsed_midi)
    song_array_path = midi.replace('MIDIs', 'SongArrays').replace('.mid', '.npy')
    np.save(song_array_path, parsed_midi)

assert len(midi_arrays) == len(midis), "MIDI arrays and # of MIDI files don't match"

# Determine how long of sequences to use for training and the seeds for the song generation
song_snippet_length_s = 5  # In seconds
sequence_length = song_snippet_length_s * ticks_per_beat

# Take the list of arrays and converting it to semi-redundant sequences based on the max length of the sequence
step_ratio_from_example = 3 / 100  # TODO: Figure out what we should be using instead
step = int(step_ratio_from_example * sequence_length)

# Get the number of X axes to be able to create the array to fill
# Doing it this way to avoid having to create a list of all the sequences and then convert it to an array which is very memory heavy
num_sequences = 0
for song in midi_arrays:
    for i in range(0, len(song) - sequence_length, step):
        num_sequences += 1

# Initialize the arrays to fill
assert (
    len(set([song.shape[1] for song in midi_arrays])) == 1
), "All songs must have the same number of pitches"
num_pitches = midi_arrays[0].shape[1]
sequences = np.zeros((num_sequences, sequence_length, num_pitches), dtype=bool)
next_notes = np.zeros((num_sequences, num_pitches), dtype=bool)

# Iterate through the songs and filling the arrays
seq_num = 0
for song in midi_arrays:
    for i in range(0, len(song) - sequence_length, step):
        sequences[seq_num] = song[i : i + sequence_length]
        next_notes[seq_num] = song[i + sequence_length]
        seq_num += 1

# Save the arrays
output_file = os.path.join(cwd, "Data\\training_data.npy")
np.save(output_file, sequences)
np.save(output_file.replace("_data.npy", "_labels.npy"), next_notes)

print("Number of sequences:", len(sequences))
print("Shape of sequences:", sequences[0].shape)
