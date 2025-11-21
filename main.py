import logging
import sys
import os
from dotenv import load_dotenv
from config import RobotConfig
from core.robot_controller import RobotController
from modules.display.display_module import DisplayModule
from modules.network.network_module import NetworkModule

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('robot.log')
    ]
)

logger = logging.getLogger(__name__)

def load_config_from_env():
    RobotConfig.NETWORK.VALORANT_API_KEY = os.getenv('VALORANT_API_KEY', '')
    RobotConfig.NETWORK.VALORANT_USERNAME = os.getenv('VALORANT_USERNAME', '')
    RobotConfig.NETWORK.VALORANT_TAG = os.getenv('VALORANT_TAG', '')
    
    if (RobotConfig.NETWORK.VALORANT_API_KEY and 
        RobotConfig.NETWORK.VALORANT_USERNAME and 
        RobotConfig.NETWORK.VALORANT_TAG):
        RobotConfig.NETWORK.VALORANT_ENABLED = True
        logger.info(f"Valorant MMR tracking enabled for {RobotConfig.NETWORK.VALORANT_USERNAME}#{RobotConfig.NETWORK.VALORANT_TAG}")
    else:
        logger.info("Valorant API credentials not configured")
        if not RobotConfig.NETWORK.VALORANT_API_KEY:
            logger.info("   Missing: VALORANT_API_KEY")
        if not RobotConfig.NETWORK.VALORANT_USERNAME:
            logger.info("   Missing: VALORANT_USERNAME")
        if not RobotConfig.NETWORK.VALORANT_TAG:
            logger.info("   Missing: VALORANT_TAG")

def main():
    logger.info("=== Starting Ada ===")

    load_config_from_env()
    
    controller = RobotController(RobotConfig)
    
    display_module = DisplayModule(RobotConfig.DISPLAY)
    controller.register_module(display_module)

    if 'network' in RobotConfig.ENABLED_MODULES:
        network_module = NetworkModule(RobotConfig.NETWORK)
        controller.register_module(network_module)
    
    try:
        controller.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        logger.info("=== Ada Stopped ===")


if __name__ == '__main__':
    main()
