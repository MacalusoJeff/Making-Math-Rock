# Converts from an array of notes to a MIDI file
# TODO: Clean this up
import os
import numpy as np
import pandas as pd
import mido

# Loading in the array of notes
cwd = os.getcwd()
generated_song_path = os.path.join(
    cwd, "Data/Outputs/GeneratedSongs/generated_song.npy"
)
song_snippet = np.load(generated_song_path, allow_pickle=True)


def reshape_array_for_note_start_end(
    arr: np.ndarray, ticks_per_beat: int = 220
) -> np.ndarray:
    """
    Find the start and end of consecutive True values in a 2D array.
    Thanks ChatGPT!
    """
    if arr.shape[1] == 127:
        arr = arr.T

    sequences = []
    for row_idx in range(arr.shape[0]):
        row = arr[row_idx]
        start, end = None, None
        for col_idx in range(arr.shape[1]):
            if row[col_idx]:
                if start is None:
                    start = col_idx
                end = col_idx
            elif start is not None:
                sequences.append((row_idx, start, end))
                start, end = None, None
        if start is not None:
            sequences.append((row_idx, start, end))
    output_array = np.array(sequences, dtype=float)

    # Converting to seconds
    output_array[:, 1] /= ticks_per_beat
    output_array[:, 2] /= ticks_per_beat

    # Ordering the array by start time
    output_array = output_array[output_array[:, 1].argsort()]
    return output_array  # (pitch, start, end)


def reshape_array_for_midi(note_start_end_array: np.ndarray) -> pd.DataFrame:
    # Formatting further to convert to MIDI
    # This is because we need the time delta between each note and if that note was a start or end
    # Using Pandas to do the remainder of the processing due to ease of use
    midi_df = pd.DataFrame(note_start_end_array, columns=["pitch", "start", "end"])
    midi_df = midi_df.melt(id_vars="pitch").rename(
        columns={"variable": "type", "value": "time"}
    )
    midi_df = midi_df.sort_values(by="time").reset_index(drop=True)
    midi_df["lagged_time"] = midi_df["time"].shift(-1)
    midi_df["time_delta"] = (midi_df["lagged_time"] - midi_df["time"]).fillna(0)
    return midi_df


def create_midi(
    df: pd.DataFrame, midi_path: str, ticks_per_beat: int = 220, tempo: int = 500000
) -> None:
    """
    TODO: Write actual docstring
    Creates a MIDI file from a dataframe of notes
    """
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
    mid.ticks_per_beat = ticks_per_beat
    for row in df.itertuples():
        if row.type == "start":
            track.append(
                mido.Message(
                    "note_on",
                    note=int(row.pitch),
                    velocity=64,
                    time=int((row.time_delta * ticks_per_beat * 2)),
                )
            )
        else:
            track.append(
                mido.Message(
                    "note_on",
                    note=int(row.pitch),
                    velocity=0,
                    time=int((row.time_delta * ticks_per_beat) * 2),
                )
            )
    mid.save(midi_path)
    print(f"MIDI file saved to {midi_path}")


song_snippet_start_ends = reshape_array_for_note_start_end(song_snippet)
song_snippet_for_output = reshape_array_for_midi(song_snippet_start_ends)
midi_output_path = generated_song_path.replace(".npy", ".mid")
create_midi(song_snippet_for_output, midi_output_path)
