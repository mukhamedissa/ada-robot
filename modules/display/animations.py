import time
from enum import Enum
from dataclasses import dataclass


class AnimationType(Enum):
    NONE = "none"
    BLINK = "blink"
    SMILE = "smile"
    HEART = "heart"
    SHAKE = "shake"
    NOD = "nod"


@dataclass
class AnimationState:
    is_active: bool = False
    start_time: float = 0
    duration: float = 0
    
    def start(self, duration: float):
        self.is_active = True
        self.start_time = time.time()
        self.duration = duration
    
    def stop(self):
        self.is_active = False
    
    def get_progress(self) -> float:
        if not self.is_active:
            return 0.0
        elapsed = time.time() - self.start_time
        return min(elapsed / self.duration, 1.0) if self.duration > 0 else 1.0
    
    def is_finished(self) -> bool:
        return self.is_active and self.get_progress() >= 1.0
