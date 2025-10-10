import numpy as np
import pygame
import time


def beep(
    frequency=440,
    duration_ms=500,
    open: bool = True,
    close: bool = True,
):
    sample_rate = 44100
    duration = duration_ms / 1000

    if open:
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=1)

    if frequency is not None:
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

        sound = pygame.sndarray.make_sound(wave)
        sound.play()

    time.sleep(duration)

    if close:
        pygame.mixer.quit()


note_frequencies_basic = {
    "C4": 261.63,
    "C#4": 277.18,
    "Db4": 277.18,
    "D4": 293.66,
    "D#4": 311.13,
    "Eb4": 311.13,
    "E4": 329.63,
    "F4": 349.23,
    "F#4": 369.99,
    "Gb4": 369.99,
    "G4": 392.00,
    "G#4": 415.30,
    "Ab4": 415.30,
    "A4": 440.00,
    "A#4": 466.16,
    "Bb4": 466.16,
    "B4": 493.88,
    "C5": 523.25,
}

note_frequencies = {}

A4_freq = 440.0
A4_midi = 69

for midi_num in range(21, 109):  # MIDI 21 (A0) to MIDI 108 (C8)
    freq = A4_freq * 2 ** ((midi_num - A4_midi) / 12)

    # MIDI note name
    octave = (midi_num // 12) - 1
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    name = note_names[midi_num % 12] + str(octave)

    note_frequencies[name] = round(freq, 2)

pirates_of_caribbean = [
    "E4",
    "G4",
    "A4",
    "A4",  # "Da da da da"
    "E4",
    "G4",
    "B4",
    "B4",  # "Da da da da"
    "E4",
    "G4",
    "A4",
    "A4",  # repeat pattern
    "G4",
    "B4",
    "A4",  # descending part
    "G4",
    "E4",
    "G4",
    "A4",  # leading up again
    "B4",
    "C5",
    "D5",
    "D5",  # climax
    "E5",
    "D5",
    "C5",
    "B4",  # descending
    "A4",
    "A4",  # ending phrase
]

no_time_to_die_notes = [
    "C5",
    "B4",
    "A4",  # "I should have known..."
    "C5",
    "B4",
    "A4",  # "I'd leave alone..."
    "G4",
    "A4",
    "A4",  # "Just goes to show..."
    "G4",
    "F4",
    "E4",  # "That the blood you bleed..."
    "E4",
    "F4",
    "G4",
    "F4",  # "is just the blood you owe..."
]

pink_panther_notes = [
    # Opening sneaky motif
    "E4",
    "G4",
    "G#4",
    "A4",
    None,
    "C5",
    "B4",
    None,
    "E4",
    "G4",
    "G#4",
    "A4",
    None,
    "B4",
    "A4",
    None,
    # Cool descending phrase
    "G#4",
    None,
    "E4",
    "G#4",
    "A4",
    None,
    "C5",
    "B4",
    None,
    # Repeat with variation
    "E4",
    "G4",
    "G#4",
    "A4",
    None,
    "C5",
    "B4",
    None,
    "E4",
    "G4",
    "G#4",
    "A4",
    None,
    "B4",
    "A4",
    None,
    # Jazzy transition
    "G#4",
    "B4",
    "C5",
    None,
    "D5",
    "C5",
    "B4",
    "A4",
    # Build up with repetition
    "E4",
    "G4",
    "G#4",
    "A4",
    None,
    "C5",
    "B4",
    None,
    "E4",
    "G4",
    "G#4",
    "A4",
    None,
    "C5",
    "B4",
    None,
    # Dramatic high end
    "F5",
    None,
    "E5",
    "D#5",
    "E5",
    None,
    "C5",
    None,
    "B4",
    "A4",
    None,
]


interstellar_notes = [
    # Opening motif (slow and atmospheric)
    "C4",
    "E4",
    "G4",
    "B4",
    "G4",
    "E4",
    "C4",
    None,
    "C4",
    "E4",
    "G4",
    "B4",
    "C5",
    "B4",
    "G4",
    None,
    # Repeats with variations
    "D4",
    "F4",
    "A4",
    "C5",
    "A4",
    "F4",
    "D4",
    None,
    "D4",
    "F4",
    "A4",
    "C5",
    "D5",
    "C5",
    "A4",
    None,
    # Rhythmic development
    "E4",
    "G4",
    "B4",
    "D5",
    "B4",
    "G4",
    "E4",
    None,
    "E4",
    "G4",
    "B4",
    "D5",
    "E5",
    "D5",
    "B4",
    None,
    # Emotional peak (play slower)
    "F4",
    "A4",
    "C5",
    "E5",
    "C5",
    "A4",
    "F4",
    None,
    "F4",
    "A4",
    "C5",
    "E5",
    "F5",
    "E5",
    "C5",
    None,
]


beep(440, 500, close=False)

for note in interstellar_notes:
    freq = note_frequencies.get(note, 440)
    beep(
        freq,
        250,
        open=False,
        close=False,
    )

beep(440, 500, open=False)
