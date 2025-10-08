# 2025 - Orvix games Tüm hakları sakıldır

import json

class ConfigManager:
    def __init__(self, logger):
        self.logger = logger
        self.config_data = {}

    def load_config(self, filename="config.json"):
        try:
            with open(filename, 'r') as f:
                self.config_data = json.load(f)
            self.logger.info(f"Konfigürasyon yüklendi: {filename}")
            return self.config_data
        except FileNotFoundError:
            self.logger.warning(f"Konfigürasyon dosyası bulunamadı: {filename}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Konfigürasyon dosyası bozuk: {filename} - {e}")
            return None

    def get_setting(self, key, default=None):
        keys = key.split('.')
        data = self.config_data
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        return data

    def save_config(self, filename="config.json"):
        try:
            with open(filename, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            self.logger.info(f"Konfigürasyon kaydedildi: {filename}")
        except Exception as e:
            self.logger.error(f"Konfigürasyon kaydetme hatası: {e}")