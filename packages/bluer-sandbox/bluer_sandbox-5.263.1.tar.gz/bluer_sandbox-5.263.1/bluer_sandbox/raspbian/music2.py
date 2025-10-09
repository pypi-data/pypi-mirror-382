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


interstellar_theme = [
    ("C4", 600),
    ("E4", 600),
    ("G4", 600),
    ("B4", 900),
    ("G4", 600),
    ("E4", 600),
    ("C4", 600),
    (None, 300),
    ("C4", 600),
    ("E4", 600),
    ("G4", 600),
    ("B4", 900),
    ("C5", 600),
    ("B4", 600),
    ("G4", 600),
    (None, 300),
    ("D4", 600),
    ("F4", 600),
    ("A4", 600),
    ("C5", 900),
    ("A4", 600),
    ("F4", 600),
    ("D4", 600),
    (None, 300),
    ("D4", 600),
    ("F4", 600),
    ("A4", 600),
    ("C5", 900),
    ("D5", 600),
    ("C5", 600),
    ("A4", 600),
    (None, 300),
    ("E4", 500),
    ("G4", 500),
    ("B4", 500),
    ("D5", 800),
    ("B4", 500),
    ("G4", 500),
    ("E4", 500),
    (None, 300),
    ("E4", 500),
    ("G4", 500),
    ("B4", 500),
    ("D5", 800),
    ("E5", 500),
    ("D5", 500),
    ("B4", 500),
    (None, 300),
    ("F4", 500),
    ("A4", 500),
    ("C5", 500),
    ("E5", 800),
    ("C5", 500),
    ("A4", 500),
    ("F4", 500),
    (None, 300),
    ("F4", 500),
    ("A4", 500),
    ("C5", 500),
    ("E5", 800),
    ("F5", 500),
    ("E5", 500),
    ("C5", 500),
    (None, 1000),
]

pink_panther_theme = [
    ("E4", 300),
    ("G4", 300),
    ("G#4", 300),
    ("A4", 600),
    (None, 200),
    ("C5", 300),
    ("B4", 500),
    (None, 300),
    ("E4", 300),
    ("G4", 300),
    ("G#4", 300),
    ("A4", 600),
    (None, 200),
    ("B4", 300),
    ("A4", 500),
    (None, 300),
    ("G#4", 300),
    (None, 150),
    ("E4", 300),
    ("G#4", 300),
    ("A4", 600),
    (None, 300),
    ("C5", 300),
    ("B4", 500),
    (None, 300),
    ("E4", 300),
    ("G4", 300),
    ("G#4", 300),
    ("A4", 600),
    (None, 200),
    ("C5", 300),
    ("B4", 500),
    (None, 300),
    ("E4", 300),
    ("G4", 300),
    ("G#4", 300),
    ("A4", 600),
    (None, 200),
    ("B4", 300),
    ("A4", 500),
    (None, 300),
    ("G#4", 300),
    ("B4", 300),
    ("C5", 300),
    (None, 200),
    ("D5", 300),
    ("C5", 300),
    ("B4", 300),
    ("A4", 500),
    (None, 300),
    ("E4", 300),
    ("G4", 300),
    ("G#4", 300),
    ("A4", 600),
    (None, 200),
    ("C5", 300),
    ("B4", 500),
    (None, 300),
    ("E4", 300),
    ("G4", 300),
    ("G#4", 300),
    ("A4", 600),
    (None, 200),
    ("C5", 300),
    ("B4", 500),
    (None, 500),
    ("F5", 300),
    (None, 150),
    ("E5", 300),
    ("D#5", 300),
    ("E5", 500),
    (None, 300),
    ("C5", 300),
    (None, 200),
    ("B4", 300),
    ("A4", 700),
]

mario_theme = [
    ("E5", 150),
    ("E5", 150),
    (None, 150),
    ("E5", 150),
    (None, 100),
    ("C5", 150),
    ("E5", 150),
    (None, 150),
    ("G5", 300),
    (None, 300),
    ("G4", 300),
    (None, 300),
    ("C5", 300),
    (None, 100),
    ("G4", 300),
    (None, 300),
    ("E4", 300),
    (None, 100),
    ("A4", 150),
    ("B4", 150),
    ("A#4", 150),
    ("A4", 150),
    ("G4", 150),
    ("E5", 150),
    ("G5", 150),
    ("A5", 300),
    (None, 300),
]

theme_1942 = [
    ("G4", 300),
    ("A4", 300),
    ("B4", 300),
    ("D5", 300),
    ("C5", 300),
    ("B4", 300),
    ("A4", 300),
    ("G4", 300),
    ("E4", 300),
    ("G4", 300),
    ("A4", 300),
    ("B4", 300),
    ("C5", 300),
    ("B4", 300),
    ("A4", 300),
    ("G4", 300),
]

no_time_to_die_theme = [
    # Verse 1: "I should have known..."
    ("C5", 800),
    ("B4", 800),
    ("A4", 1200),  # I should have known
    (None, 300),
    ("C5", 800),
    ("B4", 800),
    ("A4", 1200),  # I'd leave alone
    (None, 400),
    ("G4", 600),
    ("A4", 600),
    ("A4", 800),  # Just goes to show
    ("G4", 800),
    ("F4", 800),
    ("E4", 1200),  # that the blood you bleed
    ("E4", 800),
    ("F4", 800),
    ("G4", 1000),
    ("F4", 1000),  # is just the blood you owe
    # Verse 2: "We were a pair..."
    ("C5", 800),
    ("B4", 800),
    ("A4", 1200),
    ("A4", 600),
    ("G4", 600),
    ("F4", 800),
    ("G4", 800),
    ("E4", 800),
    ("C5", 1200),
    ("B4", 1000),
    ("A4", 1000),
    (None, 500),
    # Chorus (simplified): "Fool me once..."
    ("E4", 800),
    ("F4", 800),
    ("G4", 1000),
    ("A4", 1000),
    (None, 400),
    ("B4", 1000),
    ("C5", 1200),
    ("D5", 1000),
    ("E5", 1000),
    (None, 600),
    ("C5", 800),
    ("B4", 800),
    ("A4", 1200),
    ("G4", 1000),
    ("E4", 1000),
    (None, 1000),
]


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

for note, duration in no_time_to_die_theme:
    if note:
        freq = note_frequencies.get(note, 440)
        beep(freq, duration)
    else:
        time.sleep(duration / 1000)
