# 2025 - Orvix games Tüm hakları sakıldır

import datetime

class Logger:
    LEVELS = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
    
    def __init__(self, min_level="INFO"):
        self.min_level = self.LEVELS.get(min_level.upper(), 1)

    def _log(self, level, message):
        level_int = self.LEVELS.get(level.upper(), 1)
        if level_int >= self.min_level:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] [{level.upper()}] {message}"
            print(log_message)

    def debug(self, message): self._log("DEBUG", message)
    def info(self, message): self._log("INFO", message)
    def warning(self, message): self._log("WARNING", message)
    def error(self, message): self._log("ERROR", message)
    def critical(self, message): self._log("CRITICAL", message)