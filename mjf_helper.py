import pygame
import math
import random
from utils import resource_path

class MJFHelper:
    def __init__(self, pos, game):
        self.image = pygame.image.load(resource_path('images/mjf.jpeg')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))  # Increased size for visibility
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.game = game  # Store reference to game instance instead of dopaman
        self.speed = 3
        self.follow_distance = 100  # Distance to maintain from Dopaman
        self.recharge_range = 150   # Range within which MJF can recharge Dopaman
        self.recharge_rate = 0.5    # How much dopamine to recharge per frame
        self.block_radius = 60  # Radius within which enemies will be blocked
        self.block_cooldown = 2000  # Time in ms between blocks
        self.last_block_time = 0
        self.blocking = False
        self.block_flash_timer = 0
        self.block_flash_interval = 100  # Flash interval in ms
        self.bounce_strength = 50  # Increased bounce force
        self.bounce_radius = 80    # Protection zone size
        self.bounce_cooldown = 500  # Milliseconds between bounces
        self.last_bounce_time = 0
        self.bounce_jitter = 30    # Random angle variation
        self.protection_active = False

    def update(self):
        # Calculate distance to player using game's player_pos
        dx = self.game.player_pos[0] - self.rect.centerx
        dy = self.game.player_pos[1] - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        # Move towards player if too far, away if too close
        if distance > self.follow_distance:
            # Normalize direction and move
            dx = dx * self.speed / distance
            dy = dy * self.speed / distance
            self.rect.x += dx
            self.rect.y += dy

        # Recharge player's dopamine if in range
        if distance < self.recharge_range:
            self.game.dopamine_level = min(100, self.game.dopamine_level + self.recharge_rate)

        # Check for enemy collisions
        current_time = pygame.time.get_ticks()
        self.blocking = False
        
        for enemy in self.game.enemies[:]:  # Use slice copy to allow removal
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.block_radius:
                # Push enemy away
                if current_time - self.last_block_time > self.block_cooldown:
                    # Calculate push direction
                    if distance > 0:
                        push_dx = (dx / distance) * 50  # Push distance of 50 pixels
                        push_dy = (dy / distance) * 50
                        
                        # Update enemy position
                        enemy.pos[0] += push_dx
                        enemy.pos[1] += push_dy
                        
                        # Keep enemy within screen bounds
                        enemy.pos[0] = max(0, min(enemy.pos[0], self.game.screen_width))
                        enemy.pos[1] = max(0, min(enemy.pos[1], self.game.screen_height))
                        
                        self.blocking = True
                        self.last_block_time = current_time

        # Check for and bounce enemies
        current_time = pygame.time.get_ticks()
        self.protection_active = False
        
        for enemy in self.game.enemies:
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.bounce_radius:
                self.protection_active = True
                if distance > 0 and current_time - self.last_bounce_time > self.bounce_cooldown:
                    # Add random angle variation
                    angle = math.atan2(dy, dx)
                    angle += math.radians(random.uniform(-self.bounce_jitter, self.bounce_jitter))
                    
                    # Calculate bounce vector with randomization
                    bounce_dx = math.cos(angle) * self.bounce_strength
                    bounce_dy = math.sin(angle) * self.bounce_strength
                    
                    # Calculate new position far from current position
                    new_x = self.rect.centerx + bounce_dx * 3  # Multiply by 3 for longer bounce
                    new_y = self.rect.centery + bounce_dy * 3
                    
                    # Keep within screen bounds with wrapping
                    new_x = new_x % self.game.screen_width
                    new_y = new_y % self.game.screen_height
                    
                    # Update enemy position
                    enemy.pos[0] = new_x
                    enemy.pos[1] = new_y
                    
                    self.last_bounce_time = current_time

    def draw(self, surface):
        # Draw MJF helper
        surface.blit(self.image, self.rect)
        
        # Draw block effect when active
        if self.blocking:
            current_time = pygame.time.get_ticks()
            if (current_time // self.block_flash_interval) % 2:  # Create flashing effect
                pygame.draw.circle(surface, (255, 255, 0, 128), self.rect.center, self.block_radius, 2)
        
        # Draw protection zone when active
        if self.protection_active:
            pygame.draw.circle(surface, (255, 255, 0, 128), self.rect.center, self.bounce_radius, 2)
            # Add a glow effect
            for radius in range(self.bounce_radius - 10, self.bounce_radius, 2):
                alpha = int(128 * (1 - (self.bounce_radius - radius) / 10))
                color = (255, 255, 0, alpha)
                pygame.draw.circle(surface, color, self.rect.center, radius, 1)