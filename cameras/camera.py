import cv2
import numpy as np
from typing import Optional, List
from config import CameraConfig


class Camera:
    def __init__(self, device: int = 0, config: Optional[CameraConfig] = None):
        self.device = device
        self.config = config or CameraConfig()
        self.cap: Optional[cv2.VideoCapture] = None
        
    def start(self):
        self.cap = cv2.VideoCapture(self.device)
        if self.config.width and self.config.height:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.config.framerate)
        
    def read(self) -> Optional[np.ndarray]:
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                if self.config.rotation == 180:
                    frame = cv2.rotate(frame, cv2.ROTATE_180)
                if self.config.hflip:
                    frame = cv2.flip(frame, 1)
                if self.config.vflip:
                    frame = cv2.flip(frame, 0)
                return frame
        return None
    
    def stop(self):
        if self.cap:
            self.cap.release()
            self.cap = None


class MainLensCamera(Camera):
    def __init__(self, config: Optional[CameraConfig] = None, device: int = 0):
        super().__init__(device, config)


class FisheyeCamera(Camera):
    def __init__(self, config: Optional[CameraConfig] = None, device: int = 0):
        super().__init__(device, config)


class InfraredCamera(Camera):
    def __init__(self, config: Optional[CameraConfig] = None, device: int = 0):
        super().__init__(device, config)


def list_available_cameras() -> List[str]:
    devices = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            devices.append(f"/dev/video{i}")
            cap.release()
    return devices
