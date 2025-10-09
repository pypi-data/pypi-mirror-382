import pygame
import time
import os

from bluer_objects.env import abcli_path_git

no_time_to_die = [
    ("C5", 800),
    ("B4", 800),
    ("A4", 1200),
    (None, 300),
    ("C5", 800),
    ("B4", 800),
    ("A4", 1200),
    (None, 400),
    ("G4", 600),
    ("A4", 600),
    ("A4", 800),
    ("G4", 800),
    ("F4", 800),
    ("E4", 1200),
    ("E4", 800),
    ("F4", 800),
    ("G4", 1000),
    ("F4", 1000),
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
]


# Init pygame mixer
pygame.init()
pygame.mixer.init()

# Load all note sounds from the folder
NOTE_FOLDER = os.path.join(
    abcli_path_git,
    "piano-mp3/piano-mp3",
)
note_sounds = {}

for filename in os.listdir(NOTE_FOLDER):
    if filename.endswith(".mp3"):
        note_name = filename[:-4]  # Strip .mp3
        note_sounds[note_name] = pygame.mixer.Sound(os.path.join(NOTE_FOLDER, filename))


# Playback function
def play_melody(melody):
    for note, duration in melody:
        if note is None:
            time.sleep(duration / 1000)
        else:
            sound = note_sounds.get(note)
            if sound:
                sound.play()
            time.sleep(duration / 1000)
            sound.stop()


# Play Billie Eilish - No Time To Die (simplified)
play_melody(no_time_to_die)
