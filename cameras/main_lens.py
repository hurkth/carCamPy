from typing import Optional
from .camera import Camera
from config import CameraConfig


class MainLensCamera(Camera):
    def __init__(self, config: Optional[CameraConfig] = None):
        super().__init__("Main", config)
