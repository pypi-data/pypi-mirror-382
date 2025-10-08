# 2025 - Orvix games Tüm hakları sakıldır

import pygame

class Animation:
    def __init__(self, frames, loop=True, speed=0.1):
        self.frames = frames
        self.loop = loop
        self.speed = speed
        self.current_time = 0.0
        self.current_frame_index = 0
        self.finished = False

    def update(self, delta_time):
        if self.finished and not self.loop: return

        self.current_time += delta_time
        if self.current_time >= self.speed:
            num_frames_to_advance = int(self.current_time // self.speed)
            self.current_time = self.current_time % self.speed

            self.current_frame_index += num_frames_to_advance
            
            if self.current_frame_index >= len(self.frames):
                if self.loop:
                    self.current_frame_index %= len(self.frames)
                    self.finished = False
                else:
                    self.current_frame_index = len(self.frames) - 1
                    self.finished = True

    def get_current_frame(self):
        return self.frames[self.current_frame_index]
        
    def reset(self):
        self.current_time = 0.0
        self.current_frame_index = 0
        self.finished = False

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_frame(self, x, y, width, height, scale=1):
        frame = pygame.Surface([width, height], pygame.SRCALPHA).convert_alpha()
        frame.blit(self.sheet, (0, 0), (x, y, width, height))
        
        if scale != 1:
            size = (int(width * scale), int(height * scale))
            frame = pygame.transform.scale(frame, size)
            
        return frame