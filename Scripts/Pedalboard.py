import pedalboard
from pedalboard import (
    Pedalboard,
    Chorus,
    Reverb,
    Distortion,
    Compressor,
    Delay,
    Limiter,
)
from pedalboard.io import AudioFile
import os

cwd = os.getcwd()
output_directory = os.path.join(cwd, "Data\Outputs\GeneratedSongs")
wav_file = os.path.join(output_directory, "generated_song_6_guitar.wav")
output_wav_file = wav_file.replace(".wav", "_processed.wav")

# Make a Pedalboard object, containing multiple audio plugins:
board = Pedalboard()
# board.append(Compressor(threshold_db=-800, ratio=1, attack_ms=1.0, release_ms=100))
board.append(Distortion(drive_db=165))
board.append(Delay(delay_seconds=0.5, feedback=0, mix=0.15))
board.append(Reverb(room_size=0.75, wet_level=0.15))
# board = Pedalboard([Chorus(), Reverb(room_size=0.25)])
# board = Pedalboard([Distortion(drive_db=20), Reverb(room_size=0.95)])
board.append(pedalboard.LowpassFilter())
board.append(pedalboard.HighpassFilter())
board.append(Limiter(threshold_db=-190))
# board.append(pedalboard.PitchShift(semitones=-2))

# Open an audio file for reading, just like a regular file:
with AudioFile(wav_file) as f:

    # Open an audio file to write to:
    with AudioFile(output_wav_file, "w", f.samplerate, f.num_channels) as o:

        # Read one second of audio at a time, until the file is empty:
        while f.tell() < f.frames:
            chunk = f.read(int(f.samplerate))

            # Run the audio through our pedalboard:
            effected = board(chunk, f.samplerate, reset=False)

            # Write the output to our output file:
            o.write(effected)
