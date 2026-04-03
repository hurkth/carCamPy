import cv2
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple
import face_recognition
from datetime import datetime
from config import KNOWN_FACES_DIR, LOGS_DIR


class FaceRecognizer:
    def __init__(self, tolerance: float = 0.6):
        self.tolerance = tolerance
        self.known_encodings: List[np.ndarray] = []
        self.known_names: List[str] = []
        self._load_known_faces()

    def _load_known_faces(self):
        KNOWN_FACES_DIR.mkdir(parents=True, exist_ok=True)
        for person_dir in KNOWN_FACES_DIR.iterdir():
            if person_dir.is_dir():
                name = person_dir.name
                for img_path in person_dir.glob("*.jpg"):
                    img = face_recognition.load_image_file(img_path)
                    encodings = face_recognition.face_encodings(img)
                    if encodings:
                        self.known_encodings.append(encodings[0])
                        self.known_names.append(name)

    def register_face(self, image: np.ndarray, name: str) -> bool:
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            return False
        
        person_dir = KNOWN_FACES_DIR / name
        person_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = person_dir / f"{timestamp}.jpg"
        
        cv2.imwrite(str(img_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        
        self.known_encodings.append(encodings[0])
        self.known_names.append(name)
        return True

    def recognize(self, image: np.ndarray) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) == 3 and image.shape[2] == 3 else image
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)
        
        results = []
        for encoding, box in zip(encodings, boxes):
            matches = face_recognition.compare_faces(self.known_encodings, encoding, tolerance=self.tolerance)
            name = "Desconocido"
            
            if True in matches:
                idx = matches.index(True)
                name = self.known_names[idx]
            
            results.append((name, box))
        return results

    def draw_results(self, image: np.ndarray, results: List[Tuple[str, Tuple[int, int, int, int]]]) -> np.ndarray:
        for name, (top, right, bottom, left) in results:
            color = (0, 255, 0) if name != "Desconocido" else (0, 0, 255)
            cv2.rectangle(image, (left, top), (right, bottom), color, 2)
            cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        return image
