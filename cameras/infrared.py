from typing import Optional
from .camera import Camera
from config import CameraConfig


class InfraredCamera(Camera):
    def __init__(self, config: Optional[CameraConfig] = None):
        super().__init__("Infrared", config)
        self.filter_ir = True
        
    def enable_ir_blocking(self):
        self.filter_ir = True
        
    def disable_ir_blocking(self):
        self.filter_ir = False
