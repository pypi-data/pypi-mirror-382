# 2025 - Orvix games Tüm hakları sakıldır

class Scene:
    def __init__(self, name):
        self.name = name
        self.objects = []
        self.dynamic_objects = []
        self.static_objects = []

    def add_object(self, game_object):
        self.objects.append(game_object)
        if game_object.is_dynamic:
            self.dynamic_objects.append(game_object)
        else:
            self.static_objects.append(game_object)

    def remove_object(self, game_object):
        if game_object in self.objects:
            self.objects.remove(game_object)
            if game_object.is_dynamic:
                self.dynamic_objects.remove(game_object)
            else:
                self.static_objects.remove(game_object)
            
    def get_object(self, name):
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None
        
    def start(self):
        pass

    def stop(self):
        pass

    def update(self, delta_time, physics_manager):
        for obj in self.objects:
            obj.update(delta_time)
        
        for dynamic_obj in self.dynamic_objects:
            physics_manager.update_movement(dynamic_obj, delta_time)
            physics_manager.check_collisions(dynamic_obj, self.static_objects)

    def render(self, surface, camera, debug_mode):
        # Debug modunu GameObject'lere aktar
        for obj in self.objects:
            obj.render(surface, camera, debug_mode)