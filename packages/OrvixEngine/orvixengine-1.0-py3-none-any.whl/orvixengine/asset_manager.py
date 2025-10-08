# 2025 - Orvix games Tüm hakları sakıldır

import pygame

class AssetManager:
    def __init__(self, logger):
        self.logger = logger
        self.images = {}
        self.sounds = {}
        self.fonts = {}

    def load_image(self, name, path, alpha=True, scale=1.0):
        try:
            image = pygame.image.load(path)
            if alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()

            if scale != 1.0:
                size = (int(image.get_width() * scale), int(image.get_height() * scale))
                image = pygame.transform.scale(image, size)

            self.images[name] = image
            self.logger.debug(f"Görsel yüklendi: {name}")
            return image
        except pygame.error as e:
            self.logger.error(f"Görsel yüklenemedi: {path} - {e}")
            return None

    def get_image(self, name):
        return self.images.get(name)

    def load_font(self, name, path, size):
        try:
            font = pygame.font.Font(path, size)
            self.fonts[name] = font
            self.logger.debug(f"Font yüklendi: {name}")
        except FileNotFoundError:
            self.logger.error(f"Font dosyası bulunamadı: {path}")

    def get_font(self, name):
        return self.fonts.get(name)

    def clear(self):
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
        self.logger.info("Tüm kaynaklar temizlendi.")