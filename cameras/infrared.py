from typing import Optional
from .camera import Camera
from config import CameraConfig


class InfraredCamera(Camera):
    def __init__(self, config: Optional[CameraConfig] = None, device: int = 0):
        super().__init__(device, config)
        self.filter_ir = True
        
    def enable_ir_blocking(self):
        self.filter_ir = True
        
    def disable_ir_blocking(self):
        self.filter_ir = False
