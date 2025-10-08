# 2025 - Orvix games Tüm hakları sakıldır

import pygame

class InputManager:
    def __init__(self, logger):
        self.logger = logger
        self.key_bindings = {}
        
    def _get_key_name(self, key_code):
        return pygame.key.name(key_code).upper()

    def bind_key(self, key_name, action_callback):
        key_name = key_name.upper()
        self.key_bindings[key_name] = action_callback

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            key_name = self._get_key_name(event.key)
            if key_name in self.key_bindings:
                self.key_bindings[key_name]()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_button = event.button
            key_name = None
            if mouse_button == 1: key_name = "MOUSE_LEFT"
            elif mouse_button == 3: key_name = "MOUSE_RIGHT"
            
            if key_name and key_name in self.key_bindings:
                self.key_bindings[key_name]()