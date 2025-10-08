# 2025 - Orvix games Tüm hakları sakıldır

import pygame

class UIText:
    def __init__(self, text, x, y, font_size=30, color=(255, 255, 255)):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.font = pygame.font.Font(None, font_size)

    def render(self, surface):
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, (self.x, self.y))

class UIManager:
    def __init__(self, logger):
        pygame.font.init()
        self.logger = logger
        self.elements = []
        
    def add_element(self, element):
        self.elements.append(element)

    def update(self, delta_time):
        pass

    def render(self, surface):
        for element in self.elements:
            element.render(surface)