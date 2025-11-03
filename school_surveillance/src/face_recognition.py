from deepface import DeepFace
import cv2
import pandas as pd
from typing import List, Tuple

class FaceRecognizer:
    def __init__(self, model_name: str = "VGG-Face", distance_threshold: float = 0.4):
        self.model_name = model_name
        self.distance_threshold = distance_threshold

    def recognize_faces(self, frame, db_path: str) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        try:
            dfs = DeepFace.find(img_path=frame, db_path=db_path, model_name=self.model_name, enforce_detection=False, silent=True)
            
            recognized_faces = []
            for df in dfs:
                if not df.empty:
                    best_match = df.iloc[0]
                    identity = best_match['identity']
                    distance = best_match['distance']
                    
                    if distance < self.distance_threshold:
                        student_id = identity.split('/')[-1].split('.')[0]
                        x = int(best_match['source_x'])
                        y = int(best_match['source_y'])
                        w = int(best_match['source_w'])
                        h = int(best_match['source_h'])
                        recognized_faces.append((student_id, (y, x + w, y + h, x)))
                    else:
                        x = int(best_match['source_x'])
                        y = int(best_match['source_y'])
                        w = int(best_match['source_w'])
                        h = int(best_match['source_h'])
                        recognized_faces.append(("Unknown", (y, x + w, y + h, x)))

            return recognized_faces
        except Exception as e:
            # print(f"Error in face recognition: {e}")
            return []