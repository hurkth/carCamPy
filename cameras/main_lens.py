from typing import Optional
from .camera import Camera
from config import CameraConfig


class MainLensCamera(Camera):
    def __init__(self, config: Optional[CameraConfig] = None, device: int = 0):
        super().__init__(device, config)
