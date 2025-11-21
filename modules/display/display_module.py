import pygame
import logging
import os
import time
from modules.base_module import BaseModule
from modules.display.eyes_controller import RoboEyesController
from core.event_manager import EventType, Event

logger = logging.getLogger(__name__)


class DisplayModule(BaseModule):
    
    def __init__(self, config):
        super().__init__(config)
        self.screen = None
        self.clock = None
        self.eyes_controller = None
        self.background = None
        self.previous_rects = []
        self.running = False
        
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.assets_img_dir = os.path.join(self.project_root, "assets", "img")
        self.current_image = None
        self.display_image = False
        self.image_start_time = 0
        self.image_display_duration = 0

    def get_name(self) -> str:
        return "display"
    
    def initialize(self):
        logger.info("Initializing display module")
        
        pygame.init()
        
        flags = pygame.FULLSCREEN if self.config.FULLSCREEN else 0
        self.screen = pygame.display.set_mode(
            (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT),
            flags
        )
        pygame.mouse.set_visible(False)
        pygame.display.set_caption("Ada")
        
        self.clock = pygame.time.Clock()
        
        self.background = pygame.Surface(
            (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)
        )
        self.background.fill(self.config.BACKGROUND_COLOR)
        
        self.eyes_controller = RoboEyesController(
            self.config.SCREEN_WIDTH,
            self.config.SCREEN_HEIGHT,
            self.config
        )
        
        self._subscribe_to_events()
        
        self.running = True
        self._initialized = True
        logger.info("Display module initialized")
    
    def _subscribe_to_events(self):
        if self.event_manager:
            self.event_manager.subscribe(EventType.DISPLAY_EMOTION, self._on_emotion_event)
            self.event_manager.subscribe(EventType.DISPLAY_ANIMATION, self._on_animation_event)
            self.event_manager.subscribe(EventType.DISPLAY_LOOK, self._on_look_event)
            self.event_manager.subscribe(EventType.FACE_DETECTED, self._on_face_detected)
            self.event_manager.subscribe(EventType.DISPLAY_IMAGE, self._on_display_image)
    
    def _on_emotion_event(self, event: Event):
        emotion = event.data.get('emotion')
        logger.debug(f"Emotion event: {emotion}")
        
        if emotion == 'happy':
            self.eyes_controller.trigger_smile()
        elif emotion == 'love':
            self.eyes_controller.trigger_heart_eyes()
        elif emotion == 'surprise':
            self.eyes_controller.trigger_shake()
    
    def _on_animation_event(self, event: Event):
        animation = event.data.get('animation')
        logger.debug(f"Animation event: {animation}")
        
        if animation == 'smile':
            self.eyes_controller.trigger_smile()
        elif animation == 'shake':
            self.eyes_controller.trigger_shake()
        elif animation == 'nod':
            self.eyes_controller.trigger_nod()
        elif animation == 'heart':
            self.eyes_controller.trigger_heart_eyes()
        elif animation == 'blink':
            self.eyes_controller.trigger_blink()
    
    def _on_look_event(self, event: Event):
        direction = event.data.get('direction', 'center')
        logger.debug(f"Look event: {direction}")
        self.eyes_controller.set_look_direction(direction)
    
    def _on_face_detected(self, event: Event):
        face_position = event.data.get('position')
        if face_position:
            logger.debug(f"Face detected at {face_position}")
            self.eyes_controller.set_look_direction("center")

    def _on_display_image(self, event):
        relative_path = event.data.get('image_path')
        duration = event.data.get('duration', 0) 
        if relative_path:
            full_path = os.path.join(self.project_root, relative_path)
            if os.path.exists(full_path):
                try:
                    self.current_image = pygame.image.load(full_path)
                    self.display_image = True
                    self.image_start_time = time.time()
                    self.image_display_duration = duration
                except Exception as e:
                    print(f"Failed to load image {full_path}: {e}")
            else:
                print(f"Image file not found: {full_path}")
    
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                if self.event_manager:
                    self.event_manager.emit(EventType.SYSTEM_SHUTDOWN, source=self.get_name())
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

        if self.display_image and self.image_display_duration > 0:
            elapsed = time.time() - self.image_start_time
            if elapsed >= self.image_display_duration:
                self.display_image = False
                self.current_image = None
        
        self.eyes_controller.update()
        
        self._render()
        
        self.clock.tick(self.config.FPS)
    
    def _handle_keydown(self, key: int):
        key_actions = {
            pygame.K_q: lambda: self.event_manager.emit(EventType.SYSTEM_SHUTDOWN, source=self.get_name()),
            pygame.K_s: self.eyes_controller.trigger_smile,
            pygame.K_a: self.eyes_controller.trigger_shake,
            pygame.K_y: self.eyes_controller.trigger_nod,
            pygame.K_h: self.eyes_controller.trigger_heart_eyes,
        }
        
        action = key_actions.get(key)
        if action:
            action()
    
    def _render(self):
        current_rects = []
        if self.display_image and self.current_image:
            self.screen.blit(self.background, (0, 0))
            
            screen_width, screen_height = self.screen.get_size()
            img_width, img_height = self.current_image.get_size()
            
            scale_w = screen_width / img_width
            scale_h = screen_height / img_height
            scale = min(scale_w, scale_h)

            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            scaled_image = pygame.transform.scale(self.current_image, (new_width, new_height))
            
            pos_x = (screen_width - new_width) // 2
            pos_y = (screen_height - new_height) // 2
            
            self.screen.blit(scaled_image, (pos_x, pos_y))
            
            full_screen_rect = self.screen.get_rect()
            pygame.display.update(full_screen_rect)
            current_rects = [full_screen_rect]
        else:
            for rect in self.previous_rects:
                self.screen.blit(self.background, rect, rect)

            current_rects = self.eyes_controller.get_bounding_rects()
            self.eyes_controller.draw(self.screen)

            pygame.display.update(self.previous_rects + current_rects)
        
        self.previous_rects = current_rects


    def shutdown(self):
        logger.info("Shutting down display module")
        self.running = False
        if pygame.get_init():
            pygame.quit()
        logger.info("Display module shut down")
