#alert_manager.py
import pygame
import threading
import time
import os

class AlertManager:
    def __init__(self):
        pygame.mixer.init()  # Initializes the mixer module
        self.alert_sound = os.path.join("frontend", "assests", "alert.mp3")
        self.last_alert_time = 0  # For cooldown between alerts

    def play_alert(self):
        now = time.time()
        if now - self.last_alert_time > 60:  # Prevents alerts within 60 seconds
            threading.Thread(target=self._play).start()  # Play in background
            self.last_alert_time = now

    def _play(self):
        pygame.mixer.music.load(self.alert_sound)  # Load the sound
        pygame.mixer.music.play()  # Play it