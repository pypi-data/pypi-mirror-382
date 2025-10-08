# 2025 - Orvix games Tüm hakları sakıldır

import pygame

class Camera:
    def __init__(self, screen_width, screen_height):
        self.state = pygame.Rect(0, 0, screen_width, screen_height)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.target = None

    def apply(self, rect):
        return rect.move(self.state.topleft)

    def set_target(self, target_object):
        self.target = target_object

    def update(self):
        if self.target:
            l, t, w, h = self.target.x, self.target.y, self.target.width, self.target.height
            x = -l + self.screen_width // 2 - w // 2
            y = -t + self.screen_height // 2 - h // 2
            self.state = pygame.Rect(x, y, self.screen_width, self.screen_height)