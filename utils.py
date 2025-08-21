# utils.py

import pygame
import os
import sys

# Constants for colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
DARK_GRAY = (169, 169, 169)
CYAN = (0, 255, 255)
RETRO_BG_COLOR = BLACK

def resource_path(relative_path):
    """ Get absolute path to resource, works for development and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS.
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, 'assets', relative_path)

def render_text_wrapped(surface, text, font, color, rect, bg_color=None):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test_line = line + word + " "
        text_width, _ = font.size(test_line)
        if text_width < rect.width:
            line = test_line
        else:
            lines.append(line)
            line = word + " "
    if line:
        lines.append(line)
    
    y = rect.top
    for line in lines:
        if bg_color:
            text_surface = font.render(line.strip(), True, color, bg_color)
        else:
            text_surface = font.render(line.strip(), True, color)
        surface.blit(text_surface, (rect.left, y))
        y += font.get_linesize()

def scale_pos(x, y, scale_factor_x, scale_factor_y):
    """Helper function to scale coordinates"""
    return (int(x * scale_factor_x), int(y * scale_factor_y))

def scale_rect(rect, scale_factor_x, scale_factor_y):
    """Helper function to scale rectangles"""
    return pygame.Rect(
        rect.x * scale_factor_x,
        rect.y * scale_factor_y,
        rect.width * scale_factor_x,
        rect.height * scale_factor_y
    )

def scale_surface(surface, scale_factor_x, scale_factor_y):
    """Helper function to scale surfaces"""
    new_width = int(surface.get_width() * scale_factor_x)
    new_height = int(surface.get_height() * scale_factor_y)
    return pygame.transform.scale(surface, (new_width, new_height))
