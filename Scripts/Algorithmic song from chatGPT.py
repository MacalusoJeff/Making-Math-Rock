import os
from music21 import stream, note, duration, meter, tempo, key
import random

# Define the time signature and tempo for the song
ts = meter.TimeSignature("7/8")
mm = tempo.MetronomeMark(number=140)

# Define a list of keys
keys = ["C", "G", "D", "A", "E", "B", "F#", "Gb", "Db", "Ab", "Eb", "Bb", "F"]

# Randomly select a key
selected_key = key.Key(random.choice(keys))

# Create a stream object to hold the notes
song_stream = stream.Stream()

# Define the possible durations
possible_durations = [duration.Duration(1 / 8), duration.Duration(1 / 4)]

# Define the number of notes in the song
num_notes = 32

# Add the notes and durations to the stream object
for i in range(num_notes):
    # Select a random note and duration from the selected key
    selected_note = selected_key.pitchAndMode[0]
    selected_note = selected_note.transpose(random.randint(-12, 12))
    selected_duration = random.choice(possible_durations)

    # Create a note object with the selected note and duration
    n = note.Note()
    n.pitch = selected_note
    n.duration = selected_duration

    # Add the note object to the stream object
    song_stream.append(n)

# Set the time signature, key, and tempo of the stream object
song_stream.insert(0, ts)
song_stream.insert(0, selected_key)
song_stream.insert(0, mm)

# Write the stream object to a MIDI file
cwd = os.getcwd()
filepath = os.path.join(cwd, "Data/Outputs/chatgpt_mathrock_song.mid")
song_stream.write("midi", fp=filepath)
