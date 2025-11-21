import time
import random
import math
from modules.display.robo_eye import RoboEye
from modules.display.animations import AnimationType, AnimationState
from utils.helpers import ease_in_out


class RoboEyesController:
    
    SHAKE_DURATION = 0.8
    SHAKE_CYCLES = 2
    SHAKE_AMPLITUDE = 50
    
    NOD_DURATION = 0.5
    NOD_CYCLES = 2
    NOD_AMPLITUDE = 35
    
    LOOK_DIRECTIONS = [
        "center", "left", "right", "up", "down",
        "up-left", "down-right", "up-right"
    ]
    
    def __init__(self, screen_width: int, screen_height: int, config):
        self.config = config
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        center_y = screen_height / 2
        center_left_x = screen_width / 2 - config.EYE_WIDTH - config.EYE_GAP / 2
        center_right_x = screen_width / 2 + config.EYE_GAP / 2
        
        self.left_eye = RoboEye(
            center_left_x + config.EYE_WIDTH / 2,
            center_y,
            config.EYE_WIDTH,
            config.EYE_HEIGHT,
            config
        )
        self.right_eye = RoboEye(
            center_right_x + config.EYE_WIDTH / 2,
            center_y,
            config.EYE_WIDTH,
            config.EYE_HEIGHT,
            config
        )
        
        self.shake_state = AnimationState()
        self.nod_state = AnimationState()
        
        self.animation_queue = config.ANIMATION_CYCLE.copy()
        self.current_animation_index = 0
        self.next_animation_time = time.time() + random.uniform(*config.ANIMATION_INTERVAL)
    
    def is_special_animation_active(self) -> bool:
        return (self.shake_state.is_active or
                self.nod_state.is_active or
                self.left_eye.animations[AnimationType.SMILE].is_active or
                self.left_eye.animations[AnimationType.HEART].is_active)
    
    def trigger_smile(self):
        if not self.is_special_animation_active():
            self.left_eye.start_animation(AnimationType.SMILE)
            self.right_eye.start_animation(AnimationType.SMILE)
    
    def trigger_shake(self):
        if not self.is_special_animation_active():
            self.shake_state.start(self.SHAKE_DURATION)
    
    def trigger_nod(self):
        if not self.is_special_animation_active():
            self.nod_state.start(self.NOD_DURATION)
    
    def trigger_heart_eyes(self):
        if not (self.shake_state.is_active or self.nod_state.is_active):
            self.left_eye.start_animation(AnimationType.HEART)
            self.right_eye.start_animation(AnimationType.HEART)
    
    def trigger_blink(self):
        self.left_eye.start_animation(AnimationType.BLINK)
        self.right_eye.start_animation(AnimationType.BLINK)
    
    def set_look_direction(self, direction: str):
        target_left_x = self.left_eye.center_x - self.left_eye.width / 2
        target_left_y = self.left_eye.center_y - self.left_eye.height / 2
        target_right_x = self.right_eye.center_x - self.right_eye.width / 2
        target_right_y = self.right_eye.center_y - self.right_eye.height / 2
        
        if "left" in direction:
            target_left_x -= self.config.MAX_OFFSET_X
            target_right_x -= self.config.MAX_OFFSET_X
        
        if "right" in direction:
            target_left_x += self.config.MAX_OFFSET_X
            target_right_x += self.config.MAX_OFFSET_X
        
        if "up" in direction:
            target_left_y -= self.config.MAX_OFFSET_Y
            target_right_y -= self.config.MAX_OFFSET_Y
        
        if "down" in direction:
            target_left_y += self.config.MAX_OFFSET_Y
            target_right_y += self.config.MAX_OFFSET_Y
        
        self.left_eye.set_look_target(target_left_x, target_left_y)
        self.right_eye.set_look_target(target_right_x, target_right_y)
    
    def update(self, enable_auto_animations: bool = True):
        current_time = time.time()
        
        if self.shake_state.is_active:
            self._update_shake()
        elif self.nod_state.is_active:
            self._update_nod()
        
        if enable_auto_animations and not self.is_special_animation_active():
            self._update_automatic_actions(current_time)
        
        self.left_eye.update()
        self.right_eye.update()
    
    def _update_shake(self):
        progress = self.shake_state.get_progress()
        
        if not self.shake_state.is_finished():
            eased_progress = ease_in_out(ease_in_out(progress))
            offset = math.sin(eased_progress * self.SHAKE_CYCLES * 2 * math.pi) * self.SHAKE_AMPLITUDE
            offset *= (1.0 - progress * 0.7)
            
            self.set_look_direction("center")
            self.left_eye.target_x += offset
            self.right_eye.target_x += offset
        else:
            self.shake_state.stop()
            self.set_look_direction("center")
    
    def _update_nod(self):
        progress = self.nod_state.get_progress()
        
        if not self.nod_state.is_finished():
            eased_progress = ease_in_out(progress)
            offset = math.sin(eased_progress * self.NOD_CYCLES * 2 * math.pi) * self.NOD_AMPLITUDE
            offset *= (1.0 - progress * 0.3)
            
            self.set_look_direction("center")
            self.left_eye.target_y += offset
            self.right_eye.target_y += offset
        else:
            self.nod_state.stop()
            self.set_look_direction("center")
    
    def _update_automatic_actions(self, current_time: float):
        if current_time > self.next_animation_time:
            animation_type = self.animation_queue[self.current_animation_index]
            
            if animation_type == "blink":
                self.trigger_blink()
            elif animation_type == "look":
                direction = random.choice(self.LOOK_DIRECTIONS)
                self.set_look_direction(direction)
            elif animation_type == "smile":
                self.trigger_smile()
            elif animation_type == "shake":
                self.trigger_shake()
            elif animation_type == "nod":
                self.trigger_nod()
            
            self.current_animation_index = (self.current_animation_index + 1) % len(self.animation_queue)
            self.next_animation_time = current_time + random.uniform(*self.config.ANIMATION_INTERVAL)
    
    def draw(self, surface):
        self.left_eye.draw(surface)
        self.right_eye.draw(surface)
    
    def get_bounding_rects(self):
        return [
            self.left_eye.get_bounding_rect(),
            self.right_eye.get_bounding_rect()
        ]
