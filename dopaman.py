import pygame
import os
import sys

class Dopaman:
    def __init__(self, sprite_sheet_path, frame_rows, frame_cols, animation_speed=100):
        # Load the sprite sheet
        try:
            self.sprite_sheet = pygame.image.load(self.resource_path(sprite_sheet_path)).convert_alpha()
        except pygame.error as e:
            raise FileNotFoundError(f"Unable to load sprite sheet image at path: {sprite_sheet_path}\n{e}")

        self.frame_rows = frame_rows
        self.frame_cols = frame_cols

        self.animation_speed = animation_speed
        self.current_frame = 0
        self.last_update_time = pygame.time.get_ticks()

        # Calculate frame dimensions
        self.sheet_width, self.sheet_height = self.sprite_sheet.get_size()
        self.frame_width = self.sheet_width // self.frame_cols
        self.frame_height = self.sheet_height // self.frame_rows

        if self.sheet_width % self.frame_cols != 0 or self.sheet_height % self.frame_rows != 0:
            raise ValueError("Sprite sheet dimensions are not evenly divisible by the number of frames.")

        # Define animations
        self.animations = {
            "idle": {"row": 0, "start_col": 0, "frames": 4},  # Frames 0-3
            "walk": {"row": 0, "start_col": 4, "frames": 4}   # Frames 4-7
        }
        self.current_animation = "idle"

        self.position = (0, 0)
        self.flip = False

        self.actual_frame_col = 0  # Column index on the sprite sheet

    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def set_position(self, x, y):
        self.position = (x, y)

    def set_animation(self, animation):
        if animation in self.animations:
            if self.current_animation != animation:
                self.current_animation = animation
                self.current_frame = 0
                self.last_update_time = pygame.time.get_ticks()
        else:
            raise ValueError(f"Animation '{animation}' not defined.")

    def set_flip(self, flip):
        self.flip = flip

    def update(self):
        current_time = pygame.time.get_ticks()
        animation = self.animations[self.current_animation]
        frame_count = animation["frames"]
        start_col = animation["start_col"]

        if current_time - self.last_update_time > self.animation_speed:
            self.current_frame = (self.current_frame + 1) % frame_count
            self.last_update_time = current_time

        self.actual_frame_col = start_col + self.current_frame

    def get_frame(self, row, col):
        x = col * self.frame_width
        y = row * self.frame_height
        return self.sprite_sheet.subsurface(pygame.Rect(x, y, self.frame_width, self.frame_height))

    def draw(self, screen, scale_factor=1):
        animation = self.animations[self.current_animation]
        animation_row = animation["row"]

        frame = self.get_frame(animation_row, self.actual_frame_col)

        if scale_factor != 1:
            new_width = int(self.frame_width * scale_factor)
            new_height = int(self.frame_height * scale_factor)
            frame = pygame.transform.scale(frame, (new_width, new_height))
        else:
            new_width = self.frame_width
            new_height = self.frame_height

        if self.flip:
            frame = pygame.transform.flip(frame, True, False)

        draw_x = self.position[0] - new_width // 2
        draw_y = self.position[1] - new_height // 2

        screen.blit(frame, (draw_x, draw_y))
