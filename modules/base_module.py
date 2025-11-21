from abc import ABC, abstractmethod
from core.event_manager import EventManager
import logging

logger = logging.getLogger(__name__)


class BaseModule(ABC):
    
    def __init__(self, config):
        self.config = config
        self.event_manager: EventManager = None
        self._enabled = True
        self._initialized = False
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def initialize(self):
        pass
    
    @abstractmethod
    def update(self):
        pass
    
    @abstractmethod
    def shutdown(self):
        pass
    
    def set_event_manager(self, event_manager: EventManager):
        self.event_manager = event_manager
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def enable(self):
        self._enabled = True
    
    def disable(self):
        self._enabled = False
    
    def is_initialized(self) -> bool:
        return self._initialized
