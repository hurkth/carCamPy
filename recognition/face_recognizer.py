import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import os
from datetime import datetime
from config import KNOWN_FACES_DIR


class FaceRecognizer:
    def __init__(self, tolerance: float = 0.6):
        self.tolerance = tolerance
        self.known_faces: List[Tuple[str, np.ndarray]] = []
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self._load_known_faces()

    def _load_known_faces(self):
        KNOWN_FACES_DIR.mkdir(parents=True, exist_ok=True)
        for person_dir in KNOWN_FACES_DIR.iterdir():
            if person_dir.is_dir():
                name = person_dir.name
                for img_path in person_dir.glob("*.jpg"):
                    encoding = self._encode_face(str(img_path))
                    if encoding is not None:
                        self.known_faces.append((name, encoding))

    def _encode_face(self, image_path: str) -> Optional[np.ndarray]:
        img = cv2.imread(image_path)
        if img is None:
            return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (100, 100))
            return face.flatten()
        return None

    def register_face(self, image: np.ndarray, name: str) -> bool:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return False
        
        x, y, w, h = faces[0]
        face_gray = gray[y:y+h, x:x+w]
        face_gray = cv2.resize(face_gray, (100, 100))
        
        person_dir = KNOWN_FACES_DIR / name
        person_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = person_dir / f"{timestamp}.jpg"
        
        cv2.imwrite(str(img_path), image)
        
        self.known_faces.append((name, face_gray.flatten()))
        return True

    def recognize(self, image: np.ndarray) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        results = []
        for x, y, w, h in faces:
            face_gray = gray[y:y+h, x:x+w]
            face_gray = cv2.resize(face_gray, (100, 100))
            face_vec = face_gray.flatten()
            
            name = "Desconocido"
            min_dist = float('inf')
            
            for known_name, known_vec in self.known_faces:
                dist = np.linalg.norm(face_vec - known_vec)
                if dist < min_dist and dist < self.tolerance * 1000:
                    min_dist = dist
                    name = known_name
            
            results.append((name, (y, x+w, y+h, x)))
        
        return results

    def draw_results(self, image: np.ndarray, results: List[Tuple[str, Tuple[int, int, int, int]]]) -> np.ndarray:
        for name, (top, right, bottom, left) in results:
            color = (0, 255, 0) if name != "Desconocido" else (0, 0, 255)
            cv2.rectangle(image, (left, top), (right, bottom), color, 2)
            cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        return image
