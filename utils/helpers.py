import pygame
from typing import Tuple


def lerp(start: float, end: float, t: float) -> float:
    return start + (end - start) * t


def ease_in_out(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def draw_heart(surface: pygame.Surface, color: Tuple[int, int, int],
               x: float, y: float, size: float):
    points = [
        (x, y + size * 0.25),
        (x - size * 0.5, y - size * 0.25),
        (x - size * 0.5, y - size * 0.6),
        (x, y - size * 0.9),
        (x + size * 0.5, y - size * 0.6),
        (x + size * 0.5, y - size * 0.25),
    ]
    pygame.draw.polygon(surface, color, points)
