from typing import Callable, Dict, List, Any
from enum import Enum, auto
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    DISPLAY_EMOTION = auto()
    DISPLAY_LOOK = auto()
    DISPLAY_ANIMATION = auto()
    DISPLAY_IMAGE = auto()
    
    CAMERA_FRAME = auto()
    FACE_DETECTED = auto()
    MOTION_DETECTED = auto()
    
    AUDIO_DETECTED = auto()
    SPEECH_RECOGNIZED = auto()
    AUDIO_LEVEL = auto()
    
    SENSOR_DATA = auto()
    PROXIMITY_ALERT = auto()

    NETWORK_REQUEST = auto()
    
    SYSTEM_SHUTDOWN = auto()
    MODULE_READY = auto()
    MODULE_ERROR = auto()


@dataclass
class Event:
    event_type: EventType
    data: Any = None
    source_module: str = None


class EventManager:
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_queue: List[Event] = []
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed callback to {event_type.name}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
    
    def publish(self, event: Event):
        self._event_queue.append(event)
    
    def emit(self, event_type: EventType, data: Any = None, source: str = None):
        event = Event(event_type=event_type, data=data, source_module=source)
        self.publish(event)
    
    def process_events(self):
        while self._event_queue:
            event = self._event_queue.pop(0)
            
            if event.event_type in self._subscribers:
                for callback in self._subscribers[event.event_type]:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(f"Error in event callback: {e}", exc_info=True)
    
    def clear(self):
        self._event_queue.clear()
