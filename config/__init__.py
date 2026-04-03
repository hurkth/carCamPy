from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWN_FACES_DIR = DATA_DIR / "known_faces"
LOGS_DIR = BASE_DIR / "logs"

@dataclass
class CameraConfig:
    width: int = 640
    height: int = 480
    framerate: int = 30
    rotation: int = 0
    hflip: bool = False
    vflip: bool = False
