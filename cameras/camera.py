from picamera2 import Picamera2
import cv2
import numpy as np
from typing import Optional, List
from config import CameraConfig


class Camera:
    def __init__(self, name: str, config: Optional[CameraConfig] = None, sensor_id: int = 0):
        self.name = name
        self.config = config or CameraConfig()
        self.sensor_id = sensor_id
        self.cam: Optional[Picamera2] = None
        
    def start(self):
        from picamera2 import Picamera2
        self.cam = Picamera2(camera_name=self.name)
        self.cam.configure(self.cam.create_preview_configuration(
            main={"size": (self.config.width, self.config.height)},
            sensor=self.sensor_id
        ))
        self.cam.start()
        
    def read(self) -> Optional[np.ndarray]:
        if self.cam:
            frame = self.cam.capture_array()
            frame = cv2.rotate(frame, cv2.ROTATE_180) if self.config.rotation == 180 else frame
            if self.config.hflip:
                frame = cv2.flip(frame, 1)
            if self.config.vflip:
                frame = cv2.flip(frame, 0)
            return frame
        return None
    
    def stop(self):
        if self.cam:
            self.cam.close()
            self.cam = None


def list_available_cameras() -> List[dict]:
    import subprocess
    
    result = subprocess.run(['v4l2-ctl', '--list-devices'], capture_output=True, text=True)
    devices = []
    for line in result.stdout.split('\n'):
        if '/dev/video' in line:
            devices.append(line.strip())
    return devices
