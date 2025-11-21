import logging
import time
from typing import List, Dict
from core.event_manager import EventManager, EventType
from modules.base_module import BaseModule

logger = logging.getLogger(__name__)


class RobotController:
    
    def __init__(self, config):
        self.config = config
        self.event_manager = EventManager()
        self.modules: Dict[str, BaseModule] = {}
        self.running = False
        
        logger.info("Robot controller initialized")
    
    def register_module(self, module: BaseModule):
        module_name = module.get_name()
        if module_name in self.modules:
            logger.warning(f"Module {module_name} already registered, replacing")
        
        self.modules[module_name] = module
        module.set_event_manager(self.event_manager)
        logger.info(f"Registered module: {module_name}")
    
    def initialize_modules(self):
        for name, module in self.modules.items():
            try:
                logger.info(f"Initializing module: {name}")
                module.initialize()
                self.event_manager.emit(
                    EventType.MODULE_READY,
                    data={"module": name},
                    source="controller"
                )
            except Exception as e:
                logger.error(f"Failed to initialize module {name}: {e}", exc_info=True)
                self.event_manager.emit(
                    EventType.MODULE_ERROR,
                    data={"module": name, "error": str(e)},
                    source="controller"
                )
    
    def start(self):
        self.running = True
        self.initialize_modules()
        
        logger.info("Robot started")
        
        try:
            self.run()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.shutdown()
    
    def run(self):
        while self.running:
            for module in self.modules.values():
                if module.is_enabled():
                    try:
                        module.update()
                    except Exception as e:
                        logger.error(f"Error updating module {module.get_name()}: {e}")
            
            self.event_manager.process_events()
            
            time.sleep(0.001)
    
    def shutdown(self):
        logger.info("Shutting down robot")
        self.running = False
        
        self.event_manager.emit(EventType.SYSTEM_SHUTDOWN, source="controller")
        self.event_manager.process_events()
        
        for name, module in self.modules.items():
            try:
                logger.info(f"Shutting down module: {name}")
                module.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down module {name}: {e}")
        
        logger.info("Robot shutdown complete")
