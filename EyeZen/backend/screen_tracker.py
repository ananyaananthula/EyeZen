#screen_tracker.py
# backend/screen_tracker.py
import time

class ScreenTimeTracker:
    def __init__(self):
        self.start_time = time.time()

    def reset(self):
        self.start_time = time.time()

    def get_screen_time(self):
        elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"