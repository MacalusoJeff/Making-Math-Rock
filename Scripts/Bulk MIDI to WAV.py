import os
from midi2audio import FluidSynth

cwd = os.getcwd()
midi_dir = os.path.join(cwd, "Data/Outputs/GeneratedSongs")

# Grabbing the soundfont files for the MIDI
piano_soundfont_path = os.path.join(
    cwd,
    "Data/Soundfonts/GeneralUser GS 1.442 MuseScore/GeneralUser GS MuseScore v1.442.sf2",
)
guitar_soundfont_path = os.path.join(
    cwd,
    "Data/Soundfonts/Electric Guitar Jazz/EGuitarFSBS-bridge-jazz-small-20220911.sf2",
)

# Getting a list of the MIDI files to convert
midis = []
for filename in os.listdir(midi_dir):
    if filename.endswith(".mid") or filename.endswith(".midi"):
        midis.append(os.path.join(midi_dir, filename))

# Converting the MIDI files to WAV files
for midi in midis:
    # Saving the generated song as a WAV
    # Doing this twice - once as a piano and once as a guitar
    output_wav_piano = midi.replace(".mid", "_piano.wav")
    output_wav_guitar = output_wav_piano.replace("piano", "guitar")
    FluidSynth(sound_font=piano_soundfont_path).midi_to_audio(midi, output_wav_piano)
    FluidSynth(sound_font=guitar_soundfont_path).midi_to_audio(midi, output_wav_guitar)
