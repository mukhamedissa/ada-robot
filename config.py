import os

os.environ["DISPLAY"] = ":0"
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
os.environ['PYGAME_BLEND_ALPHA_SDL2'] = "1"


class DisplayConfig:
    SCREEN_WIDTH = 320
    SCREEN_HEIGHT = 240
    FPS = 30
    BACKGROUND_COLOR = (0, 0, 0)
    FULLSCREEN = True
    
    EYE_WIDTH = 100
    EYE_HEIGHT = 100
    EYE_GAP = 30
    EYE_COLOR = (255, 255, 255)
    
    MAX_OFFSET_X = 20
    MAX_OFFSET_Y = 15
    EYE_MOVE_SPEED = 0.2
    
    SHADOW_LAYERS = 0
    SHADOW_SPREAD = 8
    PERSPECTIVE_SHIFT = 15
    
    HEART_COLOR = (255, 105, 180)
    
    BLINK_DURATION = 0.15
    SMILE_DURATION = 0.7
    HEART_DURATION = 1.0
    SHAKE_DURATION = 0.8
    NOD_DURATION = 0.5
    
    ANIMATION_CYCLE = [
        "blink", "look", "smile", "shake", "nod",
        "blink", "look", "nod", "shake", "smile"
    ]
    ANIMATION_INTERVAL = (2, 4)


class CameraConfig:
    ENABLED = False
    DEVICE_INDEX = 0
    RESOLUTION = (640, 480)
    FPS = 30


class AudioConfig:
    ENABLED = False
    SAMPLE_RATE = 16000
    CHANNELS = 1


class SensorConfig:
    ENABLED = False
    UPDATE_RATE = 10  # Hz


class NetworkConfig:
    ENABLED = True
    
    TIMEOUT = 10
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    USE_THREAD_POOL = True
    MAX_WORKERS = 3

    VALORANT_API_KEY = ""
    VALORANT_ENABLED = True
    VALORANT_UPDATE_INTERVAL = 86400
    VALORANT_REGION = "eu"
    VALORANT_PLATFORM = "pc"
    VALORANT_USERNAME = ""
    VALORANT_TAG = ""



class RobotConfig:
    DISPLAY = DisplayConfig
    CAMERA = CameraConfig
    AUDIO = AudioConfig
    SENSOR = SensorConfig
    NETWORK = NetworkConfig
    
    ENABLED_MODULES = ['display', 'network']
