import pygame  # Ensure pygame is imported
import os

class Boss:
    def __init__(self, sprite_sheet_path, position=(0, 0), scale_factor=3, frame_rows=1, frame_cols=1, animation_speed=100, flip=False):
        """
        Initialize the boss with a sprite sheet and initial position.
        """
        self.sprite_sheet_path = sprite_sheet_path
        self.scale_factor = scale_factor
        self.position = list(position)  # Convert to list for mutability
        self.frames = []
        self.current_frame = 0
        self.frame_rows = frame_rows
        self.frame_cols = frame_cols
        self.animation_speed = animation_speed
        self.last_update = pygame.time.get_ticks()  # Track the last animation update
        self.flip = flip
        self.load_frames()
        self.jumping = False
        self.jump_timer = 0
        self.jump_duration = 4000  # Increased to 4 seconds
        self.original_y = position[1]
        self.jump_height = -500    # Higher jump
        self.jump_right_speed = 0.3  # Faster horizontal movement

    def load_frames(self):
        """
        Load frames from the sprite sheet.
        """
        sprite_sheet = pygame.image.load(self.sprite_sheet_path).convert_alpha()
        sprite_width, sprite_height = sprite_sheet.get_size()
        self.frame_width = sprite_width // self.frame_cols
        self.frame_height = sprite_height // self.frame_rows

        for row in range(self.frame_rows):
            for col in range(self.frame_cols):
                frame = sprite_sheet.subsurface(
                    (col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height)
                )
                self.frames.append(frame)

    def set_position(self, x, y):
        """Set the boss's position."""
        self.position = [x, y]

    def start_jump(self):
        """Start the jumping animation sequence"""
        self.jumping = True
        self.jump_timer = 0
        self.original_y = self.position[1]

    def update(self, delta_time):
        """Update the animation frame and position of the boss"""
        # Update animation frame
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

        # Update jump if jumping
        if self.jumping:
            self.jump_timer += delta_time
            progress = min(self.jump_timer / self.jump_duration, 1.0)
            
            # Parabolic jump motion
            self.position[1] = self.original_y + (self.jump_height * progress * (1 - progress) * 4)
            self.position[0] += self.jump_right_speed * delta_time

            # Return True if jump is complete
            return progress >= 1.0
        return False

    def draw(self, screen, scale_factor=None):
        """Render the boss."""
        frame = self.frames[self.current_frame]
        if self.flip:
            frame = pygame.transform.flip(frame, True, False)
        scale = scale_factor or self.scale_factor
        scaled_frame = pygame.transform.scale(frame, (int(self.frame_width * scale), int(self.frame_height * scale)))
        draw_x = self.position[0] - scaled_frame.get_width() // 2
        draw_y = self.position[1] - scaled_frame.get_height() // 2
        screen.blit(scaled_frame, (draw_x, draw_y))
