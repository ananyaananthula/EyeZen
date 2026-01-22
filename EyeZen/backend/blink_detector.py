# blink_detector.py
import cv2
import mediapipe as mp
import time
import math

class BlinkDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

        # Correct way to initialize FaceMesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.blink_count = 0
        self.blink_state = False
        self.blink_timestamps = []

    def get_distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def detect_blink_once(self):
        ret, frame = self.cap.read()
        if not ret:
            print("❌ Camera not accessible")
            return self.blink_count

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                top = face_landmarks.landmark[159]
                bottom = face_landmarks.landmark[145]
                left = face_landmarks.landmark[33]
                right = face_landmarks.landmark[133]

                vertical = self.get_distance(top, bottom)
                horizontal = self.get_distance(left, right)

                if horizontal == 0:
                    return self.blink_count

                ratio = vertical / horizontal

                if ratio < 0.25:
                    if not self.blink_state:
                        self.blink_count += 1
                        self.blink_state = True
                        self.blink_timestamps.append(time.time())
                else:
                    self.blink_state = False

        return self.blink_count

    def get_blinks_per_minute(self):
        now = time.time()
        self.blink_timestamps = [t for t in self.blink_timestamps if t >= now - 60]
        return len(self.blink_timestamps)

    def release(self):
        self.cap.release()
