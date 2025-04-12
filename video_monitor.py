import cv2
import mediapipe as mp
import dlib
import numpy as np
import time
import warnings
from collections import deque
from audio_cry_detect import is_crying  # Ensure this function is available and works

warnings.filterwarnings("ignore")

# MediaPipe setup
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)
pose = mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6, model_complexity=1)

# Dlib fallback
detector = dlib.get_frontal_face_detector()

# Eye landmarks
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# Thresholds
EAR_THRESH = 0.2
SLEEP_FRAME_THRESH = 10
CLOSED_FRAMES = 0

def send_alert(alert_type, message):
    print(f"ALERT [{alert_type}]: {message}")

def eye_aspect_ratio(landmarks, eye_indices):
    p = [landmarks[i] for i in eye_indices]
    hor_dist = np.linalg.norm(np.array(p[0]) - np.array(p[3]))
    ver_dist = (np.linalg.norm(np.array(p[1]) - np.array(p[5])) + np.linalg.norm(np.array(p[2]) - np.array(p[4]))) / 2
    ear = ver_dist / hor_dist
    return ear

def detect_camera_obstruction(frame, pose_results, faces):
    if not pose_results.pose_landmarks and not faces:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        if brightness < 40:
            return True
    return False

def detect_sleep_state(frame):
    global CLOSED_FRAMES
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mesh_results = face_mesh.process(rgb)

    if mesh_results.multi_face_landmarks:
        for face_landmarks in mesh_results.multi_face_landmarks:
            h, w, _ = frame.shape
            mesh_landmarks = [(int(p.x * w), int(p.y * h)) for p in face_landmarks.landmark]

            left_ear = eye_aspect_ratio(mesh_landmarks, LEFT_EYE)
            right_ear = eye_aspect_ratio(mesh_landmarks, RIGHT_EYE)
            avg_ear = (left_ear + right_ear) / 2

            if avg_ear < EAR_THRESH:
                CLOSED_FRAMES += 1
            else:
                CLOSED_FRAMES = 0

            if CLOSED_FRAMES > SLEEP_FRAME_THRESH:
                return "Sleeping"
            else:
                return "Awake"
    return "Face Not Detected"

def process_frame(frame):
    status = "Monitoring"
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    pose_results = pose.process(rgb_frame)
    faces = detector(gray_frame)

    if detect_camera_obstruction(frame, pose_results, faces):
        send_alert("CAMERA_OBSTRUCTION", "Camera is obstructed!")
        return frame, "Camera Obstructed"

    if len(faces) == 0:
        send_alert("SAFETY_CONCERN", "Cannot detect infant's face!")
        return frame, "Face Covered/Down"

    sleep_state = detect_sleep_state(frame)
    status = sleep_state

    # Check if the baby is crying and overlay it on the video
    crying_status = is_crying()
    print(f"Is crying detected: {crying_status}")  # Debugging line to check crying status
    if crying_status:
        cv2.putText(frame, "Baby is Crying", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    if crying_status and sleep_state == "Awake":
        cv2.putText(frame, "Alert: Baby Awake and Crying", (10, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        send_alert("CRYING", "Baby is awake and crying!")

    if pose_results.pose_landmarks:
        landmarks = pose_results.pose_landmarks.landmark
        hips = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].visibility
        knees = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility
        feet = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].visibility
        if hips > 0.5 and knees > 0.5 and feet > 0.5:
            status = "Uncovered Body"
            send_alert("UNCOVERED_BODY", "Infant's body is uncovered!")

        mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    return frame, status

def run_webcam_monitoring():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    fps_buffer = deque(maxlen=60)

    print("Starting Infant Monitoring System (Video Only). Press 'q' to exit.")

    while cap.isOpened():
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            send_alert("SYSTEM", "Camera feed unavailable!")
            break

        frame, status = process_frame(frame)
        fps = 1 / (time.time() - start_time)
        fps_buffer.append(fps)
        avg_fps = sum(fps_buffer) / len(fps_buffer)

        cv2.putText(frame, f"FPS: {avg_fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Status: {status}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Infant Monitoring System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_webcam_monitoring()
