import pygame
from typing import Tuple
from modules.display.animations import AnimationType, AnimationState
from utils.helpers import lerp, ease_in_out, draw_heart


class RoboEye:
    
    BLINK_DURATION = 0.15
    SMILE_DURATION = 0.7
    SMILE_HEIGHT_FACTOR = 0.6
    SMILE_TOP_RADIUS_FACTOR = 0.8
    HEART_DURATION = 1.0
    HEART_ANIMATION_PHASE = 0.3
    
    def __init__(self, center_x: float, center_y: float, width: float, height: float, config):
        self.config = config
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        
        self.current_x = center_x - width / 2
        self.current_y = center_y - height / 2
        self.current_width = width
        self.current_height = height
        
        self.target_x = self.current_x
        self.target_y = self.current_y
        
        self.original_border_radius = 20
        self._reset_border_radii()
        
        self.animations = {
            AnimationType.BLINK: AnimationState(),
            AnimationType.SMILE: AnimationState(),
            AnimationType.HEART: AnimationState(),
        }

        self.SMILE_DELAY_DURATION = 1 
        self.smile_delay_start_time = None
        
        self.heart_scale = 0.0
    
    def _reset_border_radii(self):
        self.border_top_left = self.original_border_radius
        self.border_top_right = self.original_border_radius
        self.border_bottom_left = self.original_border_radius
        self.border_bottom_right = self.original_border_radius
    
    def start_animation(self, anim_type: AnimationType):
        if anim_type == AnimationType.BLINK:
            if not self._is_any_animation_active():
                self.animations[AnimationType.BLINK].start(self.BLINK_DURATION)
        
        elif anim_type == AnimationType.SMILE:
            if not self._is_any_animation_active():
                self.animations[AnimationType.SMILE].start(self.SMILE_DURATION)
        
        elif anim_type == AnimationType.HEART:
            self._stop_all_animations()
            self.animations[AnimationType.HEART].start(self.HEART_DURATION)
    
    def _is_any_animation_active(self) -> bool:
        return any(anim.is_active for anim in self.animations.values())
    
    def _stop_all_animations(self):
        for anim in self.animations.values():
            anim.stop()
    
    def set_look_target(self, target_x: float, target_y: float):
        self.target_x = target_x
        self.target_y = target_y
    
    def update(self):
        self.current_x = lerp(self.current_x, self.target_x, self.config.EYE_MOVE_SPEED)
        self.current_y = lerp(self.current_y, self.target_y, self.config.EYE_MOVE_SPEED)
        
        if self.animations[AnimationType.HEART].is_active:
            self._update_heart_animation()
            return
        
        self.current_height = self.height
        self._reset_border_radii()
        
        if self.animations[AnimationType.BLINK].is_active:
            self._update_blink_animation()
        
        if self.animations[AnimationType.SMILE].is_active:
            self._update_smile_animation()
        
        self._update_perspective()
    
    def _update_heart_animation(self):
        anim = self.animations[AnimationType.HEART]
        progress = anim.get_progress()
        
        if progress < self.HEART_ANIMATION_PHASE:
            phase_progress = progress / self.HEART_ANIMATION_PHASE
            self.heart_scale = ease_in_out(phase_progress)
        else:
            self.heart_scale = 1.0
        
        if anim.is_finished():
            anim.stop()
            self.heart_scale = 0.0
    
    def _update_blink_animation(self):
        anim = self.animations[AnimationType.BLINK]
        progress = anim.get_progress()
        
        if progress < 0.5:
            self.current_height = self.height * (1 - progress * 2)
        else:
            self.current_height = self.height * ((progress - 0.5) * 2)
        
        if anim.is_finished():
            anim.stop()
    
    def _update_smile_animation(self):
        anim = self.animations[AnimationType.SMILE]
        progress = anim.get_progress()
        
        target_height = self.height * self.SMILE_HEIGHT_FACTOR
        target_top_radius = target_height * self.SMILE_TOP_RADIUS_FACTOR
        target_bottom_radius = self.original_border_radius * 0.5
        
        phase_duration = 1.0 / 3.0
        
        if progress < phase_duration:
            phase_progress = progress / phase_duration
            t = ease_in_out(phase_progress)
            self.current_height = lerp(self.height, target_height, t)
            self.border_bottom_left = self.border_bottom_right = lerp(
                self.original_border_radius, target_bottom_radius, t
            )
            self.border_top_left = self.border_top_right = lerp(
                self.original_border_radius, target_top_radius, t
            )
        
        elif progress < 1.0 - phase_duration:
            self.current_height = target_height
            self.border_bottom_left = self.border_bottom_right = target_bottom_radius
            self.border_top_left = self.border_top_right = target_top_radius
        
        else:
            phase_progress = (progress - (1.0 - phase_duration)) / phase_duration
            t = ease_in_out(phase_progress)
            self.current_height = lerp(target_height, self.height, t)
            self.border_bottom_left = self.border_bottom_right = lerp(
                target_bottom_radius, self.original_border_radius, t
            )
            self.border_top_left = self.border_top_right = lerp(
                target_top_radius, self.original_border_radius, t
            )
        
        if anim.is_finished():
            anim.stop()
    
    def _update_perspective(self):
        offset_from_center = (self.current_x + self.width / 2) - self.center_x
        max_h_offset = self.config.MAX_OFFSET_X
        normalized_offset = offset_from_center / max_h_offset if max_h_offset != 0 else 0
        self.current_width = self.width - abs(normalized_offset) * self.config.PERSPECTIVE_SHIFT
    
    def draw(self, surface: pygame.Surface):
        if self.animations[AnimationType.HEART].is_active and self.heart_scale > 0:
            heart_size = self.width * 0.9 * self.heart_scale
            draw_heart(surface, self.config.HEART_COLOR, self.center_x, 
                      self.center_y, heart_size)
            return
        
        draw_x = self.current_x + (self.width - self.current_width) / 2
        draw_y = self.current_y + (self.height - self.current_height) / 2
        
        self._draw_shadows(surface, draw_x, draw_y)
        
        radii = {
            'border_top_left_radius': int(self.border_top_left),
            'border_top_right_radius': int(self.border_top_right),
            'border_bottom_left_radius': int(self.border_bottom_left),
            'border_bottom_right_radius': int(self.border_bottom_right)
        }
        
        rect = pygame.Rect(draw_x, draw_y, self.current_width, self.current_height)
        pygame.draw.rect(surface, self.config.EYE_COLOR, rect, **radii)
    
    def _draw_shadows(self, surface: pygame.Surface, draw_x: float, draw_y: float):
        for i in range(self.config.SHADOW_LAYERS, 0, -1):
            layer_size = self.config.SHADOW_SPREAD * (i / self.config.SHADOW_LAYERS)
            alpha = int(40 * (i / self.config.SHADOW_LAYERS))
            
            shadow_width = self.current_width + layer_size * 2
            shadow_height = self.current_height + layer_size * 2
            shadow_surface = pygame.Surface((shadow_width, shadow_height), 
                                           pygame.SRCALPHA)
            
            radii = {
                'border_top_left_radius': int(self.border_top_left),
                'border_top_right_radius': int(self.border_top_right),
                'border_bottom_left_radius': int(self.border_bottom_left),
                'border_bottom_right_radius': int(self.border_bottom_right)
            }
            
            pygame.draw.rect(shadow_surface, (255, 255, 255, alpha),
                           shadow_surface.get_rect(topleft=(0, 0)), **radii)
            
            surface.blit(shadow_surface, (draw_x - layer_size, draw_y - layer_size))
    
    def get_bounding_rect(self) -> pygame.Rect:
        padding = self.config.SHADOW_SPREAD if self.config.SHADOW_LAYERS > 0 else 0
        draw_x = self.current_x + (self.width - self.current_width) / 2 - padding
        draw_y = self.current_y + (self.height - self.current_height) / 2 - padding
        width = self.current_width + padding * 2
        height = self.current_height + padding * 2
        return pygame.Rect(int(draw_x), int(draw_y), int(width), int(height))
