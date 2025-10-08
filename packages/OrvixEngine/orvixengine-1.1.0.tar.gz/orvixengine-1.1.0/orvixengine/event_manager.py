# 2025 - Orvix games Tüm hakları sakıldır

class EventManager:
    def __init__(self, logger):
        self.logger = logger
        self.listeners = {}

    def register_listener(self, event_name, callback):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)
        self.logger.debug(f"Event dinleyici eklendi: {event_name}")

    def unregister_listener(self, event_name, callback):
        if event_name in self.listeners and callback in self.listeners[event_name]:
            self.listeners[event_name].remove(callback)
            self.logger.debug(f"Event dinleyici kaldırıldı: {event_name}")

    def trigger_event(self, event_name, data=None):
        if event_name in self.listeners:
            self.logger.debug(f"Event tetiklendi: {event_name}")
            for callback in self.listeners[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Event '{event_name}' callback hatası: {e}")