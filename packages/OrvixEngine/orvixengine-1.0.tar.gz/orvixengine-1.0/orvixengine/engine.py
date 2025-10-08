# 2025 - Orvix games Tüm hakları sakıldır

import pygame
from .logger import Logger
from .input_manager import InputManager
from .sound_manager import SoundManager
from .physics_manager import PhysicsManager
from .scene import Scene
from .camera import Camera
from .ui_manager import UIManager
from .event_manager import EventManager
from .config_manager import ConfigManager # Yeni
from .asset_manager import AssetManager   # Yeni

class CoreEngine:
    def __init__(self, screen_width=800, screen_height=600):
        self.logger = Logger()
        
        try:
            pygame.init()
        except pygame.error as e:
            self.logger.critical(f"Pygame başlatılamadı: {e}")
            raise RuntimeError("Pygame başlatılamadı.")

        self.logger.info("Orvix Engine Başlatılıyor...")
        
        # Yeni Modüller
        self.config_manager = ConfigManager(self.logger)
        self.asset_manager = AssetManager(self.logger)
        
        self.event_manager = EventManager(self.logger)
        self.input_manager = InputManager(self.logger)
        self.sound_manager = SoundManager(self.logger)
        self.physics_manager = PhysicsManager(self.logger)
        self.ui_manager = UIManager(self.logger)
        self.camera = Camera(screen_width, screen_height)
        
        self.scenes = {}
        self.current_scene = None
        self.next_scene_name = None
        
        self.debug_mode = False
        
        self.logger.info("Çekirdek Modüller yüklendi.")
        
    def toggle_debug(self):
        self.debug_mode = not self.debug_mode
        self.logger.info(f"Debug modu: {'Açık' if self.debug_mode else 'Kapalı'}")

    def add_scene(self, scene):
        if isinstance(scene, Scene):
            if scene.name not in self.scenes:
                self.scenes[scene.name] = scene
                if self.current_scene is None:
                    self.set_scene(scene.name)
            else:
                self.logger.warning(f"Sahne zaten mevcut: {scene.name}")
        else:
            self.logger.error("Eklenmeye çalışılan nesne Scene sınıfı değil.")

    def set_scene(self, name):
        self.next_scene_name = name

    def _switch_scene_if_needed(self):
        if self.next_scene_name and self.current_scene and self.next_scene_name != self.current_scene.name:
            self.current_scene.stop()
            
        if self.next_scene_name in self.scenes:
            self.current_scene = self.scenes[self.next_scene_name]
            self.current_scene.start()
        else:
            self.logger.error(f"Sahne bulunamadı: {self.next_scene_name}")
            self.current_scene = None
        
        self.next_scene_name = None

    def update(self, delta_time):
        if self.next_scene_name:
            self._switch_scene_if_needed()
            
        self.camera.update()
        if self.current_scene:
            self.current_scene.update(delta_time, self.physics_manager)
        self.ui_manager.update(delta_time)

    def render(self, surface):
        if self.current_scene:
            self.current_scene.render(surface, self.camera, self.debug_mode)
        self.ui_manager.render(surface)