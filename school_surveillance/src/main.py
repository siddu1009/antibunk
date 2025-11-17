import json
import cv2
from typing import Dict
import socketio
import time

from .data_models import Student, Schedule, Zone
from .rule_engine import RuleEngine
from .face_recognition import FaceRecognizer
from .database import init_db, load_students, load_schedules, load_zones, save_violation
from .config import CAMERA_CONFIG_PATH, STUDENT_IMAGES_DB_PATH


def load_camera_config():
    with open(CAMERA_CONFIG_PATH, 'r') as f:
        camera_config = json.load(f)
    return camera_config


def main():
    # --- Initialization ---
    init_db()
    students = load_students()
    schedules = load_schedules()
    zones = load_zones()
    camera_config = load_camera_config()

    rule_engine = RuleEngine(students, schedules, zones, grace_period_minutes=10)
    face_recognizer = FaceRecognizer()

    # --- Connect to web viewer ---
    sio = socketio.Client()
    connected_to_web = False
    while not connected_to_web:
        try:
            sio.connect('http://localhost:5000')
            connected_to_web = True
            print("Connected to web viewer.")
        except socketio.exceptions.ConnectionError:
            print("Web viewer not available, retrying in 5 seconds...")
            time.sleep(5)

    # --- Camera setup ---
    video_captures: Dict[int, cv2.VideoCapture] = {}
    camera_zone_mapping: Dict[int, str] = {}

    for i in range(5):  # Check indices 0 to 4
        if f'camera_{i}' in camera_config:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                video_captures[i] = cap
                camera_zone_mapping[i] = camera_config[f'camera_{i}']['zone_id']
                print(f"Successfully opened camera {i} for zone {camera_zone_mapping[i]}")
            else:
                print(f"Warning: Could not open video stream for camera {i} "
                      f"(configured for zone {camera_config[f'camera_{i}']['zone_id']}). Skipping.")
        else:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                print(f"Info: Camera {i} found but not configured in camera_config.json. Skipping.")
                cap.release()

    if not video_captures:
        print("No configured cameras found or opened. Exiting.")
        if sio:
            sio.disconnect()
        return

    student_images_db_path = STUDENT_IMAGES_DB_PATH

    # --- Main loop ---
    while True:
        frames: Dict[int, cv2.Mat] = {}
        closed_cameras = []

        for camera_index, cap in video_captures.items():
            ret, frame = cap.read()
            if not ret:
                print(f"Warning: Could not read frame from camera {camera_index}. Closing camera.")
                cap.release()
                closed_cameras.append(camera_index)
            else:
                frames[camera_index] = frame

        for idx in closed_cameras:
            del video_captures[idx]
            del camera_zone_mapping[idx]

        if not video_captures:
            print("All cameras closed. Exiting.")
            if sio:
                sio.disconnect()
            break

        for camera_index, frame in frames.items():
            current_zone_id = camera_zone_mapping[camera_index]
            recognized_faces = face_recognizer.recognize_faces(frame, student_images_db_path)

            for (name, (top, right, bottom, left)) in recognized_faces:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                violation = rule_engine.process_violation(name, current_zone_id)
                if violation and sio:
                    sio.emit('new_violation', {
                        'student_id': violation.student_id,
                        'zone_id': violation.zone_id,
                        'timestamp': violation.timestamp.isoformat(),
                        'grace_period_expired': violation.grace_period_expired,
                        'alert_sent': violation.alert_sent
                    })

            cv2.imshow(f'Camera {camera_index} - Zone: {current_zone_id}', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            if sio:
                sio.disconnect()
            break

    for cap in video_captures.values():
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
    

    