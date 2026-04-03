from typing import Optional
from .camera import Camera
from config import CameraConfig


class FisheyeCamera(Camera):
    def __init__(self, config: Optional[CameraConfig] = None):
        super().__init__("Fisheye", config)
        self.dewarp = True
        
    def enable_dewarp(self):
        self.dewarp = True
        
    def disable_dewarp(self):
        self.dewarp = False
