import logging
from modules.base_module import BaseModule
from core.event_manager import EventType

logger = logging.getLogger(__name__)


class SensorModule(BaseModule):
    
    def __init__(self, config):
        super().__init__(config)
        self.sensors = {}
    
    def get_name(self) -> str:
        return "sensors"
    
    def initialize(self):
        logger.info("Initializing sensor module")
        # TODO: Initialize GPIO and sensors
        # import RPi.GPIO as GPIO
        # GPIO.setmode(GPIO.BCM)
        # Setup sensor pins...
        self._initialized = True
        logger.info("Sensor module initialized")
    
    def update(self):
        # TODO: Read sensor values
        # proximity = self.read_proximity_sensor()
        # if proximity < threshold:
        #     self.event_manager.emit(
        #         EventType.PROXIMITY_ALERT,
        #         data={'distance': proximity},
        #         source=self.get_name()
        #     )
        pass
    
    def shutdown(self):
        logger.info("Shutting down sensor module")
        # TODO: Cleanup GPIO
        # GPIO.cleanup()
        logger.info("Sensor module shut down")
