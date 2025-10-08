# 2025 - Orvix games Tüm hakları sakıldır

import pygame

class SoundManager:
    def __init__(self, logger):
        pygame.mixer.init()
        self.logger = logger
        self.sounds = {}
        self.music_volume = 0.5
        self.sound_volume = 0.8
        
        pygame.mixer.music.set_volume(self.music_volume)

    def load_sound(self, name, path):
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
            self.sounds[name].set_volume(self.sound_volume)
        except pygame.error as e:
            self.logger.error(f"Ses yüklenemedi: {name} - {e}")

    def play_sound(self, name, loops=0):
        if name in self.sounds:
            self.sounds[name].play(loops)

    def play_music(self, path, loop=True):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1 if loop else 0)
        except pygame.error as e:
            self.logger.error(f"Müzik yüklenemedi/çalınamadı: {path} - {e}")
            
    def stop_music(self):
        pygame.mixer.music.stop()

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)