# 2025 - Orvix games Tüm hakları sakıldır

import pygame
from .animation import Animation

class GameObject:
    def __init__(self, name, x=0, y=0, width=32, height=32, color=None, is_dynamic=False, can_move=True, tag="default"):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.color = color
        
        self.tag = tag.lower()
        self.is_dynamic = is_dynamic
        self.can_move = can_move
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        self.rect = pygame.Rect(self.x, self.y, width, height)
        
        self.animations = {}
        self.current_animation = None
        self.image = None
        
    def add_animation(self, name, frames, loop=True, speed=0.1):
        self.animations[name] = Animation(frames, loop, speed)

    def set_animation(self, name):
        if name in self.animations:
            if self.current_animation != self.animations[name]:
                self.current_animation = self.animations[name]
                self.current_animation.reset()
        
    def update(self, delta_time):
        if self.current_animation:
            self.current_animation.update(delta_time)
            self.image = self.current_animation.get_current_frame()
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            self.rect.width = self.width
            self.rect.height = self.height
            
    def render(self, surface, camera, debug_mode=False):
        render_rect = camera.apply(self.rect)
        
        if self.image:
            surface.blit(self.image, render_rect.topleft)
        elif self.color:
            pygame.draw.rect(surface, self.color, render_rect)
        
        if debug_mode:
            border_color = (255, 0, 255) if self.is_dynamic else (255, 255, 0)
            pygame.draw.rect(surface, border_color, render_rect, 1) 
            
    def on_collision(self, other_object):
        pass