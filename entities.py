# entities.py

import pygame
import random
from utils import RED, DARK_GRAY, scale_rect, scale_pos

class Enemy:
    def __init__(self, name, speed, x, y, screen_width, screen_height):
        self.name = name
        self.speed = speed
        self.pos = [x, y]  # Initialize the position with x and y coordinates
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.size = 30  # Add this to avoid errors related to missing attributes
        self.rect = pygame.Rect(self.pos[0] - 15, self.pos[1] - 15, 30, 30)  # Use rect to avoid conflict with property

    def move(self, player_pos, walls):
        # Calculate movement logic here...
        new_x, new_y = self.pos[0], self.pos[1]

        # Move towards player
        if self.pos[0] < player_pos[0]:
            new_x += self.speed
        elif self.pos[0] > player_pos[0]:
            new_x -= self.speed

        if self.pos[1] < player_pos[1]:
            new_y += self.speed
        elif self.pos[1] > player_pos[1]:
            new_y -= self.speed

        # Create a new rectangle for the new position
        new_rect = pygame.Rect(new_x - 15, new_y - 15, 30, 30)

        # Check wall collision and ensure within screen boundaries
        if not self.check_wall_collision(new_rect, walls) and 0 <= new_rect.left <= self.screen_width and 0 <= new_rect.top <= self.screen_height:
            self.pos = [new_x, new_y]
            self.rect = new_rect  # Update rect to match the new position

    def check_wall_collision(self, rect, walls):
        for wall in walls:
            if rect.colliderect(wall):
                return True
        return False

class Star:
    def __init__(self, screen_width, screen_height):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.1, 0.5)
        self.screen_width = screen_width
        self.screen_height = screen_height

    def move(self):
        self.y += self.speed
        if self.y > self.screen_height:
            self.y = 0
            self.x = random.randint(0, self.screen_width)
