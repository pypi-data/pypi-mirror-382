import pygame

pygame.init()

# Load piano note WAVs (e.g., "C4.wav", "D4.wav", etc.)
note_sounds = {
    "C4": pygame.mixer.Sound("piano/C4.wav"),
    "D4": pygame.mixer.Sound("piano/D4.wav"),
    # ...
}

note_sounds["C4"].play()
