# 2025 - Orvix games Tüm hakları sakıldır

import pygame
from .logger import Logger

class PhysicsManager:
    def __init__(self, logger, gravity=(0, 980)):
        self.logger = logger
        self.gravity = gravity

    def update_movement(self, obj, delta_time):
        if not obj.can_move:
            return

        if obj.is_dynamic:
            obj.velocity_x += self.gravity[0] * delta_time
            obj.velocity_y += self.gravity[1] * delta_time

        new_x = obj.x + obj.velocity_x * delta_time
        new_y = obj.y + obj.velocity_y * delta_time
        
        obj.x = new_x
        obj.y = new_y
        obj.rect.x = int(obj.x)
        obj.rect.y = int(obj.y)

    def check_collisions(self, dynamic_object, static_objects):
        if not dynamic_object.is_dynamic:
            return

        old_rect = dynamic_object.rect.copy()
        dynamic_object.rect.x = int(dynamic_object.x)
        dynamic_object.rect.y = int(dynamic_object.y)

        for static_obj in static_objects:
            if static_obj.tag == "solid" and dynamic_object.rect.colliderect(static_obj.rect):
                dynamic_object.on_collision(static_obj)
                static_obj.on_collision(dynamic_object)
                
                dynamic_object.x = old_rect.x
                dynamic_object.y = old_rect.y
                dynamic_object.rect.x = old_rect.x
                dynamic_object.rect.y = old_rect.y
                
                dynamic_object.velocity_x = 0
                dynamic_object.velocity_y = 0
                
            elif static_obj.tag == "trigger" and dynamic_object.rect.colliderect(static_obj.rect):
                 dynamic_object.on_collision(static_obj)
                 static_obj.on_collision(dynamic_object)