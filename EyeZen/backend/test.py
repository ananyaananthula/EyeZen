import cv2
import mediapipe as mp
import time
import math

# Initialize MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

# Webcam
cap = cv2.VideoCapture(0)

# Blink detection variables
blink_count = 0
blink_state = False
blink_timestamps = []

# Distance between 2 points
def get_distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

# Blink detection loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Eye landmarks (top-bottom & left-right)
            top = face_landmarks.landmark[159]
            bottom = face_landmarks.landmark[145]
            left = face_landmarks.landmark[33]
            right = face_landmarks.landmark[133]

            vertical_dist = get_distance(top, bottom)
            horizontal_dist = get_distance(left, right)
            ratio = vertical_dist / horizontal_dist

            # Detect blink
            if ratio < 0.25:
                if not blink_state:
                    blink_count += 1
                    blink_state = True
                    blink_timestamps.append(time.time())
            else:
                blink_state = False

    # Calculate BPM
    now = time.time()
    one_min_ago = now - 60
    blink_timestamps = [t for t in blink_timestamps if t >= one_min_ago]
    bpm = len(blink_timestamps)

    # Show output
    cv2.putText(frame, f"Blinks: {blink_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"BPM: {bpm}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.imshow("Blink Rate Monitor", frame)

    # Quit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
