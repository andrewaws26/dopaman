# game.py

import pygame
import sys
import random
import math  # Add this import
from utils import *
from entities import Enemy, Star
from cutscenes import show_level_story
from dopaman import Dopaman
import utils
from utils import scale_surface
from mjf_helper import MJFHelper

class Game:
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.set_num_channels(8)

        # Initialize game variables
        self.screen_width = 800
        self.screen_height = 600
        self.num_collectibles = {
            "dopamine": 2,
            "medicine": 1,
            "levodopa": 1,
            "dbs": 1,
            "stress_management": 2,
            "mirapex": 1,
            "super_speed": 1,
            "shield": 1
        }
        self.window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Dopaman")
        self.game_surface = pygame.Surface(self.window_size)
        self.clock = pygame.time.Clock()
        self.running = True
        self.level = 1
        self.lives = 5
        self.score = 0
        self.high_score = self.load_high_score()
        self.dopaman = Dopaman(resource_path("images/dopaman.png"), frame_rows=1, frame_cols=8, animation_speed=100)
        self.dopaman_scale_factor = 1.2  # Increased from 0.7
        self.dopamine_level = 100
        self.dopamine_depletion_rate = 0.05
        self.initial_player_speed = 5
        self.reduced_speed = 3
        self.player_speed = self.initial_player_speed
        self.player_pos = [self.screen_width // 2, self.screen_height // 2]
        self.difficulty_settings = {
            "Easy": {"depletion_rate": 0.04, "enemy_speed": 1.0},
            "Medium": {"depletion_rate": 0.05, "enemy_speed": 1.5},
            "Hard": {"depletion_rate": 0.06, "enemy_speed": 2.0}
        }
        self.selected_difficulty = "Medium"
        self.enemy_speed = self.difficulty_settings[self.selected_difficulty]["enemy_speed"]
        self.dopamine_depletion_rate = self.difficulty_settings[self.selected_difficulty]["depletion_rate"]
        self.load_assets()
        self.base_radius = 15  # Decreased from 20 to make collectibles smaller
        self.base_label_offset = 15  # Adjusted from 10
        self.init_game_state()
        self.is_fullscreen = False
        # Get the current display info for native resolution
        self.display_info = pygame.display.Info()
        self.native_width = self.display_info.current_w
        self.native_height = self.display_info.current_h
        self.scale_factor_x = 1
        self.scale_factor_y = 1
        self.last_direction = 'right'
        self.game_paused = False
        self.damage_animation_active = False
        self.damage_animation_timer = 0
        self.damage_animation_duration = 1000
        self.damage_flash_interval = 100
        self.confused_active = False
        self.confused_timer = 0
        self.tremor_active = False
        self.super_speed_active = False
        self.super_speed_timer = 0
        self.levodopa_active = False
        self.levodopa_timer = 0
        self.dbs_active = False
        self.dbs_timer = 0
        self.shield_active = False
        self.shield_timer = 0
        self.particles = []
        self.mjf_helper_speed = 2.0
        self.mjf_helper_pos = [random.randint(0, self.screen_width), random.randint(0, self.screen_height)]
        self.mjf_helper_radius = 100
        self.walls = []
        self.generate_walls()
        self.dopamine_collectibles = []
        self.medicine_collectibles = []
        self.levodopa_collectibles = []
        self.dbs_collectibles = []
        self.stress_management_collectibles = []
        self.mirapex_collectibles = []
        self.super_speed_collectibles = []
        self.shield_collectibles = []
        self.collectibles = []
        self.sounds = {}
        self.sounds['collect'] = pygame.mixer.Sound(utils.resource_path("sounds/collect_sound.mp3"))
        self.sounds['game_over'] = pygame.mixer.Sound(utils.resource_path("sounds/game_over.mp3"))
        self.EDUCATIONAL_CONTENT = {
            1: [
                "Parkinson's Disease:",
                "A progressive nervous system disorder that affects movement.",
                "It occurs when brain cells that make dopamine stop working.",
                "",
                "This causes tremors, stiffness, and balance problems."
            ],
            2: [
                "The Role of Dopamine:",
                "A vital neurotransmitter that controls",
                "movement and emotional responses.",
                "It helps regulate the brain's",
                "reward system and motor function.",
                "",
                "In Parkinson's disease,",
                "dopamine levels gradually decrease."
            ],
            3: [
                "Early Symptoms:",
                "- Tremor in hands, arms, legs, or face",
                "- Muscle stiffness",
                "- Slow movement (bradykinesia)",
                "- Poor balance and coordination"
            ],
            3: [
                "Power Up!",
                "Micheal J. Fox will assist you by",
                "recharging your dopamine and blocking",
                "enemies from hurting you"
            ],
            4: [
                "Treatment: Medications",
                "Levodopa is converted to dopamine in the brain,",
                "helping to control movement symptoms.",
                "",
                "Other medications like Mirapex can also help."
            ],
            5: [
                "Advanced Treatments:",
                "Deep Brain Stimulation (DBS) can help control",
                "tremors and reduce medication needs.",
                "",
                "It uses electrical impulses to regulate brain signals."
            ],
            # Add more levels as needed
        }
        self.stars = [Star(self.screen_width, self.screen_height) for _ in range(100)]
        self.uniform_scale = 1
        self.base_font_size = 24  # Increased from 16
        self.base_small_font_size = 20  # Increased from 12
        self.base_radius = 15  # Decreased from 20 to make collectibles smaller
        self.base_label_offset = 15  # Adjusted from 10
        self.safe_spawn_radius = 200  # Minimum safe distance for respawning

    def load_assets(self):
        # Load images, sounds, fonts
        try:
            dopaman_image = pygame.image.load(resource_path('images/dopaman.png')).convert_alpha()
            scale_factor = 2  # Adjust this factor as needed
            new_width = int(dopaman_image.get_width() * scale_factor)
            new_height = int(dopaman_image.get_height() * scale_factor)
            self.dopaman_image = pygame.transform.scale(dopaman_image, (new_width, new_height))
            self.mjf_helper_image = pygame.image.load(resource_path("images/mjf.jpeg")).convert_alpha()
            self.enemy_image = pygame.image.load(resource_path("images/enemy.png")).convert_alpha()
            # Load fonts
            self.retro_font = pygame.font.Font(resource_path("fonts/PressStart2P.ttf"), 32)
            self.retro_small_font = pygame.font.Font(resource_path("fonts/PressStart2P.ttf"), 16)
            self.game_font = pygame.font.SysFont("Arial", 28)
            # Load sounds
            self.collect_sound = utils.pygame.mixer.Sound(resource_path("sounds/collect_sound.mp3"))
            self.game_over_sound = utils.pygame.mixer.Sound(resource_path("sounds/game_over.mp3"))
            self.sounds = {
                'collect': self.collect_sound,
                'game_over': self.game_over_sound
            }
            # Load and play background music
            pygame.mixer.music.load(resource_path("sounds/background_music.mp3"))
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Error loading assets: {e}")
            pygame.quit()
            sys.exit()

    def load_high_score(self):
        try:
            with open(resource_path('high_score.txt'), 'r') as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        try:
            with open(resource_path('high_score.txt'), 'w') as f:
                f.write(str(self.high_score))
        except:
            print("Could not save high score")

    def init_game_state(self):
        # Initialize game state variables
        self.enemies = []
        self.generate_walls()
        self.create_enemies()
        # Initialize collectibles
        self.generate_collectibles()
        # Other initializations
        self.tremor_active = False
        self.super_speed_active = False
        self.super_speed_timer = 0
        self.levodopa_active = False
        self.levodopa_timer = 0
        self.dbs_active = False
        self.dbs_timer = 0
        self.shield_active = False
        self.shield_timer = 0
        self.particles = []
        self.mjf_helper_pos = [random.randint(0, self.screen_width), random.randint(0, self.screen_height)]

    def generate_walls(self):
        """Generate walls for each level with specific, designed layouts"""
        self.walls = []
        wall_layouts = {
            1: [  # Tutorial level - Simple open layout with safe zones
                (100, 100, 50, 150),    # Left upper barrier
                (650, 100, 50, 150),    # Right upper barrier
                (100, 350, 50, 150),    # Left lower barrier
                (650, 350, 50, 150),    # Right lower barrier
                (300, 250, 200, 30),    # Center platform
            ],
            2: [  # Learning curves and corridors
                (150, 100, 30, 400),    # Left main wall
                (620, 100, 30, 400),    # Right main wall
                (150, 250, 150, 30),    # Left platform
                (500, 250, 150, 30),    # Right platform
                (350, 400, 100, 30),    # Bottom platform
            ],
            3: [  # Diamond pattern with strategic paths
                (400, 50, 30, 100),     # Top vertical
                (250, 200, 30, 100),    # Left middle
                (550, 200, 30, 100),    # Right middle
                (400, 350, 30, 100),    # Bottom vertical
                (250, 200, 300, 30),    # Upper horizontal
                (250, 300, 300, 30),    # Lower horizontal
            ],
            4: [  # Maze-like pattern with multiple routes
                (150, 100, 200, 30),    # Top left
                (450, 100, 200, 30),    # Top right
                (150, 100, 30, 200),    # Left wall upper
                (620, 100, 30, 200),    # Right wall upper
                (300, 250, 200, 30),    # Middle platform
                (150, 400, 30, 100),    # Left wall lower
                (620, 400, 30, 100),    # Right wall lower
                (150, 470, 200, 30),    # Bottom left
                (450, 470, 200, 30),    # Bottom right
            ],
            5: [  # Advanced layout with strategic zones
                (200, 50, 400, 30),     # Top barrier
                (100, 150, 30, 300),    # Left wall
                (670, 150, 30, 300),    # Right wall
                (200, 250, 150, 30),    # Left platform
                (450, 250, 150, 30),    # Right platform
                (300, 350, 200, 30),    # Lower middle platform
                (200, 520, 400, 30),    # Bottom barrier
            ]
        }

        # Get layout for current level or generate procedural layout for higher levels
        if self.level <= 5:
            current_layout = wall_layouts[self.level]
        else:
            # Procedurally generate more complex layouts for higher levels
            current_layout = self.generate_procedural_layout()

        # Create safe zone around player spawn
        player_safe_zone = pygame.Rect(
            self.screen_width // 2 - 100,
            self.screen_height // 2 - 100,
            200, 200
        )

        # Add walls that don't intersect with safe zone
        for wall_spec in current_layout:
            wall = pygame.Rect(*wall_spec)
            if not wall.colliderect(player_safe_zone):
                self.walls.append(wall)

    def generate_procedural_layout(self):
        """Generate procedural wall layouts for higher levels"""
        layout = []
        num_walls = 8 + self.level  # Increase number of walls with level
        
        for _ in range(num_walls):
            # Generate wall dimensions
            width = random.choice([30, 150, 200])
            height = random.choice([30, 100, 150])
            
            # Generate position, ensuring walls aren't too close to edges
            x = random.randint(50, self.screen_width - width - 50)
            y = random.randint(50, self.screen_height - height - 50)
            
            # Ensure walls don't completely block paths
            valid_position = True
            for existing_wall in layout:
                ex_x, ex_y, ex_w, ex_h = existing_wall
                if (abs(x - ex_x) < 100 and abs(y - ex_y) < 100):
                    valid_position = False
                    break
            
            if valid_position:
                layout.append((x, y, width, height))
        
        return layout

    def check_wall_collision(self, rect):
        """Check if the given rectangle collides with any walls."""
        for wall in self.walls:
            if rect.colliderect(wall):
                print(f"Collision with wall: {wall}")  # Debugging output
                return True
        return False

    def generate_collectibles(self):
        """Generate collectibles with proper collision checking."""
        attempt = 0
        max_attempts = 100
        collectible_radius = self.base_radius
        
        for collectible_type, num in self.num_collectibles.items():
            collectibles = []
            while len(collectibles) < num and attempt < max_attempts:
                x = random.randint(collectible_radius, self.screen_width - collectible_radius)
                y = random.randint(collectible_radius, self.screen_height - collectible_radius)
                collectible_rect = pygame.Rect(x - collectible_radius, y - collectible_radius, 
                                             collectible_radius * 2, collectible_radius * 2)

                # Check if it collides with walls
                wall_collision = False
                for wall in self.walls:
                    if wall.colliderect(collectible_rect):
                        wall_collision = True
                        break

                # Check other collectibles to prevent overlap
                too_close_to_others = False
                for other in collectibles:
                    other_x, other_y = other
                    distance = ((x - other_x) ** 2 + (y - other_y) ** 2) ** 0.5
                    if distance < collectible_radius * 2:
                        too_close_to_others = True
                        break

                if not wall_collision and not too_close_to_others:
                    collectibles.append([x, y])
                else:
                    attempt += 1

            # Set the appropriate collectible list based on type
            if collectible_type == "dopamine":
                self.dopamine_collectibles = collectibles
            elif collectible_type == "medicine":
                self.medicine_collectibles = collectibles
            elif collectible_type == "levodopa":
                self.levodopa_collectibles = collectibles
            elif collectible_type == "dbs":
                self.dbs_collectibles = collectibles
            elif collectible_type == "stress_management":
                self.stress_management_collectibles = collectibles
            elif collectible_type == "mirapex":
                self.mirapex_collectibles = collectibles
            elif collectible_type == "super_speed":
                self.super_speed_collectibles = collectibles
            elif collectible_type == "shield":
                self.shield_collectibles = collectibles

            if attempt >= max_attempts:
                print(f"Warning: Could not place all {collectible_type} collectibles after {max_attempts} attempts")

    def run(self):
        # Main game loop
        self.start_screen()
        self.start_game()

    def handle_events(self):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.pause()
                if event.key == pygame.K_f:  # Changed from K_f to K_F11
                    self.toggle_fullscreen()
                if event.key == pygame.K_ESCAPE and self.is_fullscreen:  # Add ESC key to exit fullscreen
                    self.toggle_fullscreen()
                if event.key == pygame.K_RETURN:
                    if self.game_paused:
                        self.game_paused = False

    def update(self):
        # Update game state
        self.dopaman.update()
        self.apply_movement()
        self.move_enemies()
        self.move_mjf_helper()
        self.check_collectible_collision()
        self.apply_enemy_effects()
        self.check_game_over()
        if self.dopamine_level <= 0:
            self.game_over()
        # Deplete dopamine
        self.dopamine_level -= self.dopamine_depletion_rate
        # Handle power-up timers
        if self.super_speed_active and pygame.time.get_ticks() - self.super_speed_timer > 5000:
            self.super_speed_active = False
        if self.shield_active and pygame.time.get_ticks() - self.shield_timer > 5000:
            self.shield_active = False
        if self.confused_active and pygame.time.get_ticks() - self.confused_timer > 5000:
            self.confused_active = False
        # Check if level is complete
        if self.check_level_complete():
            self.level += 1
            self.next_level()
            return

        # Update MJF helper if present
        if hasattr(self, 'mjf_helper') and self.level >= 1:
            self.mjf_helper.update()

    # game.py

    def draw(self):
        """Draw all game elements directly on the screen."""
        # Clear the game surface
        self.game_surface.fill(RETRO_BG_COLOR)

        # Draw walls directly on the game surface
        self.draw_walls()

        # Draw enemies directly on the game surface
        self.draw_enemies()

        # Draw Michael J. Fox helper directly on the game surface
        self.draw_mjf_helper()

        # Draw collectibles directly on the game surface
        self.draw_collectibles()

        # Draw player (Dopaman) directly on the game surface
        self.draw_player()

        # Update particles directly on the game surface
        self.update_particles()

        # Draw power-up status directly on the game surface
        self.draw_power_up_status()

        # Draw dopamine bar directly on the game surface
        self.draw_dopamine_bar()

        # Draw lives directly on the game surface
        self.draw_lives()

        # Draw level directly on the game surface
        self.draw_level()

        # Draw score directly on the game surface
        self.draw_score()

        # Draw high score directly on the game surface
        self.draw_high_score()

        # Scale the game surface to match the screen size and update the display
        scaled_surface = pygame.transform.scale(self.game_surface, self.window_size)
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    def apply_movement(self):
        keys = pygame.key.get_pressed()
        speed = self.reduced_speed if self.dopamine_level < 40 else self.player_speed

        if self.super_speed_active:
            speed *= 1.5

        # Determine movement direction
        if self.confused_active:
            x_direction = keys[pygame.K_LEFT] - keys[pygame.K_RIGHT]
            y_direction = keys[pygame.K_UP] - keys[pygame.K_DOWN]
        else:
            x_direction = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
            y_direction = keys[pygame.K_DOWN] - keys[pygame.K_UP]

        # Set player moving state
        self.player_is_moving = x_direction != 0 or y_direction != 0

        # Update last_direction based on x_direction
        if x_direction > 0:
            self.last_direction = 'right'
        elif x_direction < 0:
            self.last_direction = 'left'
        # If x_direction is 0, keep last_direction as is

        # Calculate proposed new position
        new_x = self.player_pos[0] + x_direction * speed
        new_y = self.player_pos[1] + y_direction * speed

        # Create a rectangle for the player's new position
        new_rect = pygame.Rect(new_x - 15, new_y - 15, 30, 30)  # Adjusted size to better match sprite

        # Check for collisions with walls
        if not self.check_wall_collision(new_rect):
            # Update player position only if no collision
            if 0 <= new_rect.left and new_rect.right <= self.screen_width:  # Horizontal boundaries
                self.player_pos[0] = new_x
            else:
                print("Horizontal boundary collision")

            if 0 <= new_rect.top and new_rect.bottom <= self.screen_height:  # Vertical boundaries
                self.player_pos[1] = new_y
            else:
                print("Vertical boundary collision")
        else:
            print("Collision detected with wall.")

        # Apply tremor effect if dopamine level is low and DBS is inactive
        if not self.dbs_active:
            self.tremor_active = self.dopamine_level < 30
        if self.tremor_active:
            self.player_pos[0] += random.choice([-1, 1])
            self.player_pos[1] += random.choice([-1, 1])

    def pause(self):
        # Implement pause screen
        self.game_paused = True
        pygame.mixer.music.pause()
        while self.game_paused:
            self.game_surface.fill(RETRO_BG_COLOR)
            pause_text = self.retro_font.render("PAUSED", True, YELLOW)
            pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.game_surface.blit(pause_text, pause_rect)
            instruction_text = self.retro_small_font.render("Press 'P' to Resume", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
            self.game_surface.blit(instruction_text, instruction_rect)
            scaled_surface = pygame.transform.scale(self.game_surface, self.screen.get_size())
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        pygame.mixer.music.unpause()
                        self.game_paused = False
                    if event.key == pygame.K_f:
                        self.toggle_fullscreen()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
    def apply_enemy_effects(self):
        """
        Apply the effects of any enemies that collide with the player.
        This function will handle reducing dopamine levels, slowing down the player, etc.
        """
        # Define the player's collision rectangle
        player_rect = pygame.Rect(self.player_pos[0] - 20, self.player_pos[1] - 30, 40, 60)

        # Iterate over each enemy and check for collisions
        for enemy in self.enemies:
            if player_rect.colliderect(enemy.rect):
                # If the player's shield is not active, apply enemy effects
                if not self.shield_active:
                    if enemy.name == "Depression":
                        # Reduce dopamine level due to collision with "Depression"
                        self.dopamine_level -= self.dopamine_depletion_rate
                        if self.dopamine_level <= 0:
                            # If dopamine level hits zero, game over
                            self.game_over()
                            return
                    elif enemy.name == "Anxiety":
                        # Slow down the player due to "Anxiety" enemy
                        self.player_speed = self.reduced_speed
                    elif enemy.name == "Fatigue":
                        # Reduce dopamine level due to "Fatigue"
                        self.dopamine_level -= 0.5
                    elif enemy.name == "Stress":
                        # Set confused effect to True due to "Stress"
                        self.confused_active = True
                        self.confused_timer = pygame.time.get_ticks()

                # If shield is active, reduce the enemy's impact or add additional logic if needed.
                # e.g., destroy the enemy or reduce its damage effect.

    def toggle_fullscreen(self):
        # Toggle fullscreen state
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            # Save the current window size before going fullscreen
            self.windowed_size = self.screen.get_size()
            # Set to native resolution for fullscreen
            self.screen = pygame.display.set_mode((self.native_width, self.native_height), pygame.FULLSCREEN)
        else:
            # Return to windowed mode with previous size
            self.screen = pygame.display.set_mode(self.window_size)

        # Update scaling factors
        current_size = self.screen.get_size()
        self.scale_factor_x = current_size[0] / self.screen_width
        self.scale_factor_y = current_size[1] / self.screen_height
        self.uniform_scale = min(self.scale_factor_x, self.scale_factor_y)

        # Update the window size
        self.window_size = current_size

    def move_enemies(self):
        for enemy in self.enemies:
            enemy.move(self.player_pos, self.walls)

    def move_mjf_helper(self):
        # Update to use MJF helper class if it exists
        if hasattr(self, 'mjf_helper') and self.level >= 1:
            self.mjf_helper.update()

    def check_collectible_collision(self):
        """Check if the player has collided with any collectibles and handle effects."""
        # Define a rectangle for the player's current position (used to detect collision)
        player_rect = pygame.Rect(self.player_pos[0] - 20, self.player_pos[1] - 30, 40, 60)
        
        # Check collision with dopamine collectibles
        for collectible in self.dopamine_collectibles[:]:
            if player_rect.collidepoint(collectible):
                # Remove the collected item from the list of collectibles
                self.dopamine_collectibles.remove(collectible)
                
                # Increase dopamine level and update score
                self.dopamine_level = min(100, self.dopamine_level + 20)
                self.score += 20
                
                # Create particle effect at the collectible's position
                self.create_particles(collectible, GREEN)
                
                # Play the collect sound effect if available
                if self.sounds.get('collect'):
                    print("Dopamine collectible gathered, playing sound...")
                    self.sounds['collect'].play()

        # Check collision with medicine collectibles
        for medicine in self.medicine_collectibles[:]:
            if player_rect.collidepoint(medicine):
                self.medicine_collectibles.remove(medicine)
                
                # Increase dopamine level and disable tremor
                self.dopamine_level = min(100, self.dopamine_level + 30)
                self.tremor_active = False
                self.score += 30

                # Create particle effect at the collectible's position
                self.create_particles(medicine, YELLOW)

                # Play the collect sound effect if available
                if self.sounds.get('collect'):
                    print("Medicine collectible gathered, playing sound...")
                    self.sounds['collect'].play()

        # Check collision with levodopa collectibles
        for levodopa in self.levodopa_collectibles[:]:
            if player_rect.collidepoint(levodopa):
                self.levodopa_collectibles.remove(levodopa)

                # Apply levodopa effects
                self.levodopa_effect()

                # Create particle effect at the collectible's position
                self.create_particles(levodopa, PURPLE)

                # Play the collect sound effect if available
                if self.sounds.get('collect'):
                    print("Levodopa collectible gathered, playing sound...")
                    self.sounds['collect'].play()

        # Check collision with DBS (Deep Brain Stimulation) collectibles
        for dbs in self.dbs_collectibles[:]:
            if player_rect.collidepoint(dbs):
                self.dbs_collectibles.remove(dbs)

                # Apply DBS effect
                self.dbs_effect()

                # Create particle effect at the collectible's position
                self.create_particles(dbs, ORANGE)

                # Play the collect sound effect if available
                if self.sounds.get('collect'):
                    print("DBS collectible gathered, playing sound...")
                    self.sounds['collect'].play()

        # Check collision with stress management collectibles
        for stress in self.stress_management_collectibles[:]:
            if player_rect.collidepoint(stress):
                self.stress_management_collectibles.remove(stress)

                # Apply stress management effect
                self.stress_management_effect()

                # Create particle effect at the collectible's position
                self.create_particles(stress, BROWN)

                # Play the collect sound effect if available
                if self.sounds.get('collect'):
                    print("Stress management collectible gathered, playing sound...")
                    self.sounds['collect'].play()

        # Check collision with mirapex collectibles
        for mirapex in self.mirapex_collectibles[:]:
            if player_rect.collidepoint(mirapex):
                self.mirapex_collectibles.remove(mirapex)

                # Apply mirapex effect
                self.mirapex_effect()

                # Create particle effect at the collectible's position
                self.create_particles(mirapex, BLUE)

                # Play the collect sound effect if available
                if self.sounds.get('collect'):
                    print("Mirapex collectible gathered, playing sound...")
                    self.sounds['collect'].play()

        # Check collision with super speed collectibles
        for speed in self.super_speed_collectibles[:]:
            if player_rect.collidepoint(speed):
                self.super_speed_collectibles.remove(speed)

                # Apply super speed effect
                self.super_speed_effect()

                # Create particle effect at the collectible's position
                self.create_particles(speed, CYAN)

                # Play the collect sound effect if available
                if self.sounds.get('collect'):
                    print("Super speed collectible gathered, playing sound...")
                    self.sounds['collect'].play()

        # Check collision with shield collectibles
        for shield in self.shield_collectibles[:]:
            if player_rect.collidepoint(shield):
                self.shield_collectibles.remove(shield)

                # Apply shield effect
                self.shield_effect()

                # Create particle effect at the collectible's position
                self.create_particles(shield, WHITE)

                # Play the collect sound effect if available
                if self.sounds.get('collect'):
                    print("Shield collectible gathered, playing sound...")
                    self.sounds['collect'].play()

    def check_game_over(self):
        player_rect = pygame.Rect(self.player_pos[0] - 20, self.player_pos[1] - 30, 40, 60)
        collision_occurred = False

        for enemy in self.enemies:
            enemy_rect = enemy.rect
            if player_rect.colliderect(enemy_rect):
                if not self.shield_active:
                    self.lives -= 1
                    self.create_particles(self.player_pos, RED)
                    collision_occurred = True
                    self.play_death_animation()

                    if self.lives <= 0:
                        self.game_over()
                    else:
                        # Reset player position and state
                        self.player_pos[0], self.player_pos[1] = self.screen_width // 2, self.screen_height // 2
                        self.tremor_active = False
                        self.confused_active = False
                        self.shield_active = False

                        # Create safe zone before respawning
                        self.ensure_safe_spawn()

        if collision_occurred and self.lives <= 0:
            # Save high score
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

            # End game
            self.running = False

    def ensure_safe_spawn(self):
        """Create a safe zone for player respawn by moving enemies away."""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        for enemy in self.enemies:
            # Calculate distance from spawn point
            dx = enemy.pos[0] - center_x
            dy = enemy.pos[1] - center_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < self.safe_spawn_radius:
                # Move enemy outside safe zone
                if distance > 0:
                    # Calculate new position
                    angle = math.atan2(dy, dx)
                    new_x = center_x + math.cos(angle) * self.safe_spawn_radius
                    new_y = center_y + math.sin(angle) * self.safe_spawn_radius
                    
                    # Add some randomness to prevent enemies clustering
                    new_x += random.uniform(-50, 50)
                    new_y += random.uniform(-50, 50)
                    
                    # Keep within screen bounds
                    enemy.pos[0] = max(0, min(new_x, self.screen_width))
                    enemy.pos[1] = max(0, min(new_y, self.screen_height))

    def check_level_complete(self):
        # Check if all collectible lists are empty
        return (len(self.dopamine_collectibles) == 0 and
                len(self.medicine_collectibles) == 0 and
                len(self.levodopa_collectibles) == 0 and
                len(self.dbs_collectibles) == 0 and
                len(self.stress_management_collectibles) == 0 and
                len(self.mirapex_collectibles) == 0 and
                len(self.super_speed_collectibles) == 0 and
                len(self.shield_collectibles) == 0)

    def next_level(self):
    # Display the story for the new level
        show_level_story(
        game_surface=self.game_surface,
        screen=self.screen,
        level=self.level,
        EDUCATIONAL_CONTENT=self.EDUCATIONAL_CONTENT,
        retro_font=self.retro_font,
        retro_small_font=self.retro_small_font,
        retro_bg_color=RETRO_BG_COLOR,
        player_image=self.dopaman_image,
        mjf_helper_image=self.mjf_helper_image,
        enemy_image=self.enemy_image
        )

        # Adjust game variables based on the new level
        self.enemy_speed *= 1.05
        self.player_speed = self.initial_player_speed * (1.02 ** (self.level - 1))
        self.score += 100

        # Generate walls for the new level
        self.generate_walls()

        # Generate collectibles after walls are created
        self.generate_collectibles()

        # Set Michael J. Fox helper position if level is 3 or higher
        if self.level >= 3:
            mjf_start_pos = [
                random.randint(0, self.screen_width),
                random.randint(0, self.screen_height)
            ]
            self.mjf_helper = MJFHelper(mjf_start_pos, self)

        # Create enemies for the new level
        self.create_enemies()

    def game_over(self):
        pygame.mixer.music.stop()
        # Play game over sound if available
        if self.sounds.get('game_over'):
            self.sounds['game_over'].play()

        clock = pygame.time.Clock()
        game_over_displayed = True
        while game_over_displayed:
            self.game_surface.fill(RETRO_BG_COLOR)
            game_over_text = self.retro_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
            self.game_surface.blit(game_over_text, game_over_rect)

            score_text = self.game_font.render(f"Score: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.game_surface.blit(score_text, score_rect)

            high_score_text = self.game_font.render(f"High Score: {self.high_score}", True, WHITE)
            high_score_rect = high_score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
            self.game_surface.blit(high_score_text, high_score_rect)

            instruction_text = self.retro_small_font.render("Press Enter to Restart or Esc to Quit", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
            self.game_surface.blit(instruction_text, instruction_rect)

            scaled_surface = pygame.transform.scale(self.game_surface, self.screen.get_size())
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game_over_displayed = False
                        self.restart_game()
                        self.running = True  # Set running to True to restart the game
                    elif event.key == pygame.K_ESCAPE:
                        game_over_displayed = False
                        self.running = False  # Set running to False to exit
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def restart_game(self):
        pygame.mixer.music.play(-1)  # Restart music when game restarts
        self.dopamine_level = 100
        self.level = 1
        self.lives = 3
        self.score = 0
        self.tremor_active = False
        self.player_speed = self.initial_player_speed
        self.player_pos = [self.screen_width // 2, self.screen_height // 2]
        self.generate_walls()
        self.create_enemies()
        self.generate_collectibles()
        self.running = True  # Set running to True to restart the game loop

    def start_screen(self):
        self.show_prologue()
        clock = pygame.time.Clock()
        blink = True
        blink_timer = 0

        # Create stars specifically for the start screen
        stars = [Star(self.screen_width, self.screen_height) for _ in range(100)]

        while True:
            # Fill background with the retro color
            self.game_surface.fill(RETRO_BG_COLOR)

            # Draw moving stars
            for star in stars:
                star.move()
                pygame.draw.circle(self.game_surface, WHITE, (int(star.x), int(star.y)), star.size)

            # Render the title text
            title_text = self.retro_font.render("DOPAMAN", True, GREEN)
            title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
            self.game_surface.blit(title_text, title_rect)

            # Render blinking instruction text
            if blink:
                instruction_text = self.retro_small_font.render("Press Enter to Start", True, WHITE)
                instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.game_surface.blit(instruction_text, instruction_rect)

            # Render high score
            high_score_text = self.retro_small_font.render(f'HIGH SCORE: {self.high_score}', True, WHITE)
            high_score_rect = high_score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
            self.game_surface.blit(high_score_text, high_score_rect)

            # Toggle blinking effect
            blink_timer += clock.get_time()
            if blink_timer >= 500:
                blink = not blink
                blink_timer = 0

            # Render the scaled game surface
            scaled_surface = pygame.transform.scale(self.game_surface, self.screen.get_size())
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            clock.tick(60)

            # Handle input events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.difficulty_selection()
                        self.tutorial_screen()
                        return  # Exit the start screen
                    if event.key == pygame.K_f:
                        self.toggle_fullscreen()


    def show_prologue(self):
        clock = pygame.time.Clock()
        showing_prologue = True
        story_text = [
            "In the depths of the human brain,",
            "a heroic neurotransmitter named Dopaman",
            "fights a constant battle against",
            "the forces of neurodegeneration.",
            "",
            "As Parkinson's disease threatens",
            "to disrupt the delicate balance",
            "of the nervous system,",
            "",
            "Dopaman must collect vital resources",
            "and avoid the symptoms that seek",
            "to diminish his power.",
            "",
            "With the help of Michael J. Fox,",
            "a beacon of hope and courage,",
            "Dopaman strives to maintain harmony",
            "in the neural networks.",
            "",
            "Press Enter to begin your mission..."
        ]

        fade_alpha = 0
        fade_speed = 2
        text_surfaces = []
        text_positions = []

        # Pre-render text
        y_offset = 100 * self.scale_factor_y
        for line in story_text:
            text_surface = self.retro_small_font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset))
            text_surfaces.append(text_surface)
            text_positions.append(text_rect)
            y_offset += 30 * self.scale_factor_y

        while showing_prologue:
            self.game_surface.fill(RETRO_BG_COLOR)

            # Draw text with fade effect
            for surface, pos in zip(text_surfaces, text_positions):
                temp_surface = surface.copy()
                temp_surface.set_alpha(fade_alpha)
                self.game_surface.blit(temp_surface, pos)

            # Fade in
            if fade_alpha < 255:
                fade_alpha = min(255, fade_alpha + fade_speed)

            scaled_surface = pygame.transform.scale(self.game_surface, self.window_size)
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        showing_prologue = False
                    if event.key == pygame.K_f:
                        self.toggle_fullscreen()

    def get_scaled_text_positions(self, total_height, line_spacing):
        """Helper method to calculate scaled text positions"""
        available_height = self.screen.get_height()
        start_y = (available_height - total_height) // 2
        return start_y, line_spacing * self.scale_factor_y

    def difficulty_selection(self):
        clock = pygame.time.Clock()
        selecting = True
        difficulties = ["Easy", "Medium", "Hard"]
        selected_index = 1

        # Calculate font sizes based on screen height
        title_size = min(32, int(self.screen_height * 0.05))  # 5% of screen height
        option_size = min(16, int(self.screen_height * 0.025))  # 2.5% of screen height

        # Create appropriately sized fonts
        title_font = pygame.font.Font(resource_path("fonts/PressStart2P.ttf"), title_size)
        option_font = pygame.font.Font(resource_path("fonts/PressStart2P.ttf"), option_size)

        while selecting:
            self.game_surface.fill(RETRO_BG_COLOR)
            
            screen_center_x = self.screen_width // 2
            screen_height = self.screen_height
            
            # Title position - 20% from the top
            title_y = int(screen_height * 0.2)
            title_text = title_font.render("SELECT DIFFICULTY", True, GREEN)
            title_rect = title_text.get_rect(center=(screen_center_x, title_y))
            self.game_surface.blit(title_text, title_rect)

            # Calculate positions for difficulty options
            spacing = int(screen_height * 0.1)  # 10% of screen height
            start_y = screen_height // 2 - (len(difficulties) * spacing) // 2
            
            for i, diff in enumerate(difficulties):
                y_pos = start_y + i * spacing
                if i == selected_index:
                    diff_text = option_font.render(f"> {diff} <", True, YELLOW)
                else:
                    diff_text = option_font.render(diff, True, WHITE)
                diff_rect = diff_text.get_rect(center=(screen_center_x, y_pos))
                self.game_surface.blit(diff_text, diff_rect)

            # Instructions at the bottom
            instruction_text = option_font.render("Use UP/DOWN arrows and ENTER to select", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(screen_center_x, screen_height * 0.8))
            self.game_surface.blit(instruction_text, instruction_rect)

            # Scale and display
            scaled_surface = pygame.transform.scale(self.game_surface, self.window_size)
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            clock.tick(60)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(difficulties)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(difficulties)
                    elif event.key == pygame.K_RETURN:
                        self.selected_difficulty = difficulties[selected_index]
                        self.enemy_speed = self.difficulty_settings[self.selected_difficulty]["enemy_speed"]
                        self.dopamine_depletion_rate = self.difficulty_settings[self.selected_difficulty]["depletion_rate"]
                        selecting = False
                    elif event.key == pygame.K_f:
                        self.toggle_fullscreen()

    def tutorial_screen(self):
        clock = pygame.time.Clock()
        showing_tutorial = True
        tutorial_text = [
            "HOW TO PLAY",
            "",
            "Move Dopaman with arrow keys.",
            "Collect items to boost dopamine.",
            "Avoid enemies: Stress, Anxiety, etc.",
            "Use power-ups to gain advantages.",
            "Press 'P' to pause the game.",
            "Press F to toggle fullscreen",
            "",
            "Press Enter to continue..."
        ]

        # Calculate font sizes based on screen height
        title_size = min(32, int(self.screen_height * 0.05))  # 5% of screen height
        text_size = min(16, int(self.screen_height * 0.025))  # 2.5% of screen height

        # Create appropriately sized fonts
        title_font = pygame.font.Font(resource_path("fonts/PressStart2P.ttf"), title_size)
        text_font = pygame.font.Font(resource_path("fonts/PressStart2P.ttf"), text_size)

        while showing_tutorial:
            self.game_surface.fill(RETRO_BG_COLOR)
            
            screen_center_x = self.screen_width // 2
            screen_height = self.screen_height
            
            # Calculate spacing and starting position
            line_height = int(screen_height * 0.06)  # 6% of screen height
            total_height = len(tutorial_text) * line_height
            start_y = (screen_height - total_height) // 2
            
            # Draw each line of text
            for i, line in enumerate(tutorial_text):
                y_pos = start_y + (i * line_height)
                if i == 0:  # Title text
                    text_surface = title_font.render(line, True, GREEN)
                else:  # Regular text
                    text_surface = text_font.render(line, True, WHITE)
                text_rect = text_surface.get_rect(center=(screen_center_x, y_pos))
                self.game_surface.blit(text_surface, text_rect)

            # Scale and display
            scaled_surface = pygame.transform.scale(self.game_surface, self.window_size)
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            clock.tick(60)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        showing_tutorial = False
                        return
                    elif event.key == pygame.K_f:
                        self.toggle_fullscreen()

    def start_game(self):
        self.running = True
        self.level = 1
        self.next_level()
        
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()  # No arguments needed

    def create_particles(self, position, color):
        for _ in range(10):
            self.particles.append([[position[0], position[1]], [random.uniform(-1, 1), random.uniform(-1, 1)], random.randint(2, 4), color])

    def update_particles(self):
        for particle in self.particles[:]:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.1
            if particle[2] <= 0:
                self.particles.remove(particle)
            else:
                pygame.draw.circle(self.game_surface, particle[3], (int(particle[0][0]), int(particle[0][1])), int(particle[2]))

    def draw_walls(self):
        for wall in self.walls:
            pygame.draw.rect(self.game_surface, DARK_GRAY, wall)  # Draw wall fill
            pygame.draw.rect(self.game_surface, RED, wall, 2)    # Draw wall border

    def draw_enemies(self):
        label_offset = int(20 * self.uniform_scale * 0.6)
        for enemy in self.enemies:
            scaled_pos = (enemy.pos[0] * self.scale_factor_x, enemy.pos[1] * self.scale_factor_y)
            label = self.game_font.render(enemy.name, True, RED)
            label_rect = label.get_rect(center=(scaled_pos[0], scaled_pos[1] - label_offset))
            self.game_surface.blit(label, label_rect)

    def draw_mjf_helper(self):
        if hasattr(self, 'mjf_helper') and self.level >= 1:
            self.mjf_helper.draw(self.game_surface)
            
            # Draw helper info
            if self.mjf_helper.blocking:
                text = self.game_font.render("Blocking!", True, YELLOW)
                text_rect = text.get_rect(center=(
                    self.mjf_helper.rect.centerx,
                    self.mjf_helper.rect.top - 20
                ))
                self.game_surface.blit(text, text_rect)

    def draw_collectibles(self):
        scaled_radius = int(self.base_radius * self.uniform_scale)  # Removed the 0.6 multiplier to keep full size
        label_offset = int(self.base_label_offset * self.uniform_scale)  # Removed the 0.6 multiplier
        
        for collectible in self.dopamine_collectibles[:]:
            scaled_pos = (collectible[0] * self.scale_factor_x, collectible[1] * self.scale_factor_y)
            pygame.draw.circle(self.game_surface, GREEN, scaled_pos, scaled_radius)
            label = self.game_font.render("Dopamine", True, WHITE)
            label_rect = label.get_rect(center=(scaled_pos[0], scaled_pos[1] - label_offset))
            self.game_surface.blit(label, label_rect)
        
        # Apply the same pattern for other collectibles
        for medicine in self.medicine_collectibles[:]:
            scaled_pos = (medicine[0] * self.scale_factor_x, medicine[1] * self.scale_factor_y)
            pygame.draw.circle(self.game_surface, YELLOW, scaled_pos, scaled_radius)
            label = self.game_font.render("Medicine", True, WHITE)
            label_rect = label.get_rect(center=(scaled_pos[0], scaled_pos[1] - label_offset))
            self.game_surface.blit(label, label_rect)
        for levodopa in self.levodopa_collectibles[:]:
            scaled_pos = (levodopa[0] * self.scale_factor_x, levodopa[1] * self.scale_factor_y)
            pygame.draw.circle(self.game_surface, PURPLE, scaled_pos, scaled_radius)
            label = self.game_font.render("Levodopa", True, WHITE)
            label_rect = label.get_rect(center=(scaled_pos[0], scaled_pos[1] - label_offset))
            self.game_surface.blit(label, label_rect)
        for dbs in self.dbs_collectibles[:]:
            scaled_pos = (dbs[0] * self.scale_factor_x, dbs[1] * self.scale_factor_y)
            pygame.draw.circle(self.game_surface, ORANGE, scaled_pos, scaled_radius)
            label = self.game_font.render("DBS", True, WHITE)
            label_rect = label.get_rect(center=(scaled_pos[0], scaled_pos[1] - label_offset))
            self.game_surface.blit(label, label_rect)
        for stress in self.stress_management_collectibles[:]:
            scaled_pos = (stress[0] * self.scale_factor_x, stress[1] * self.scale_factor_y)
            pygame.draw.circle(self.game_surface, BROWN, scaled_pos, scaled_radius)
            label = self.game_font.render("Stress Mgmt", True, WHITE)
            label_rect = label.get_rect(center=(scaled_pos[0], scaled_pos[1] - label_offset))
            self.game_surface.blit(label, label_rect)
        for mirapex in self.mirapex_collectibles[:]:
            scaled_pos = (mirapex[0] * self.scale_factor_x, mirapex[1] * self.scale_factor_y)
            pygame.draw.circle(self.game_surface, BLUE, scaled_pos, scaled_radius)
            label = self.game_font.render("Mirapex", True, WHITE)
            label_rect = label.get_rect(center=(scaled_pos[0], scaled_pos[1] - label_offset))
            self.game_surface.blit(label, label_rect)
        for speed in self.super_speed_collectibles[:]:
            scaled_pos = (speed[0] * self.scale_factor_x, speed[1] * self.scale_factor_y)
            pygame.draw.circle(self.game_surface, CYAN, scaled_pos, scaled_radius)
            label = self.game_font.render("Super Speed", True, WHITE)
            label_rect = label.get_rect(center=(scaled_pos[0], scaled_pos[1] - label_offset))
            self.game_surface.blit(label, label_rect)
        for shield in self.shield_collectibles[:]:
            scaled_pos = (shield[0] * self.scale_factor_x, shield[1] * self.scale_factor_y)
            pygame.draw.circle(self.game_surface, WHITE, scaled_pos, scaled_radius)
            label = self.game_font.render("Shield", True, RED)
            label_rect = label.get_rect(center=(scaled_pos[0], scaled_pos[1] - label_offset))
            self.game_surface.blit(label, label_rect)

    def draw_player(self):
        """Draw the Dopaman character on the game surface."""
        scaled_pos = (self.player_pos[0] * self.scale_factor_x, self.player_pos[1] * self.scale_factor_y)
        self.dopaman.set_position(scaled_pos[0], scaled_pos[1])
        
        # Use the player_is_moving variable set in apply_movement
        moving = self.player_is_moving
        
        # Set the appropriate animation
        if moving:
            self.dopaman.set_animation("walk")
        else:
            self.dopaman.set_animation("idle")
        
        # Set the flip attribute based on last_direction
        if self.last_direction == 'left':
            self.dopaman.set_flip(True)
        else:
            self.dopaman.set_flip(False)
        
        # Update and draw Dopaman with scale_factor
        self.dopaman.update()
        self.dopaman.draw(self.game_surface, scale_factor=self.dopaman_scale_factor)

        # Draw shield effect if shield is active
        if self.shield_active:
            shield_radius = int(25 * self.uniform_scale)  # Adjusted shield size
            pygame.draw.circle(self.game_surface, RED, (int(scaled_pos[0]), int(scaled_pos[1])), shield_radius, 2)  # Reduced from 40,3

    def draw_power_up_status(self):
        x_offset = 50 * self.scale_factor_x
        y_offset = (self.screen_height - 40) * self.scale_factor_y
        font_size = int(self.base_font_size * self.uniform_scale)
        game_font = pygame.font.SysFont("Arial", font_size)

        if self.super_speed_active:
            remaining_time = max(0, (5000 - (pygame.time.get_ticks() - self.super_speed_timer)) // 1000)
            label = game_font.render(f"Super Speed: {remaining_time}s", True, CYAN)
            self.game_surface.blit(label, (x_offset, y_offset))
            x_offset += label.get_width() + 20 * self.scale_factor_x
        if self.shield_active:
            remaining_time = max(0, (5000 - (pygame.time.get_ticks() - self.shield_timer)) // 1000)
            label = game_font.render(f"Shield: {remaining_time}s", True, RED)
            self.game_surface.blit(label, (x_offset, y_offset))
            x_offset += label.get_width() + 20 * self.scale_factor_x
    # ...add other power-ups as needed...

    def draw_dopamine_bar(self):
        margin = 10 * self.scale_factor_x
        bar_width = self.dopamine_level * 2 * self.scale_factor_x
        bar_height = 20 * self.scale_factor_y
        
        # Draw bar
        pygame.draw.rect(self.game_surface, BLUE, (margin, margin, bar_width, bar_height))
        
        # Draw text
        font_size = int(self.base_font_size * self.uniform_scale)
        game_font = pygame.font.SysFont("Arial", font_size)
        dopamine_text = game_font.render(f"Dopamine: {int(self.dopamine_level)}%", True, WHITE)
        text_rect = dopamine_text.get_rect(left=margin, top=bar_height + margin * 2)
        self.game_surface.blit(dopamine_text, text_rect)

    def draw_lives(self):
        margin = 10 * self.scale_factor_x
        font_size = int(self.base_font_size * self.uniform_scale)
        game_font = pygame.font.SysFont("Arial", font_size)
        lives_text = game_font.render(f"Lives: {self.lives}", True, WHITE)
        text_rect = lives_text.get_rect(
            right=self.screen_width * self.scale_factor_x - margin, 
            top=margin
        )
        self.game_surface.blit(lives_text, text_rect)

    def draw_level(self):
        font_size = int(self.base_font_size * self.uniform_scale)
        game_font = pygame.font.SysFont("Arial", font_size)
        level_text = game_font.render(f"Level: {self.level}", True, WHITE)
        text_rect = level_text.get_rect(
            centerx=self.screen_width // 2 * self.scale_factor_x, 
            top=10 * self.scale_factor_y
        )
        self.game_surface.blit(level_text, text_rect)

    def draw_score(self):
        margin = 10 * self.scale_factor_x
        font_size = int(self.base_font_size * self.uniform_scale)
        game_font = pygame.font.SysFont("Arial", font_size)
        score_text = game_font.render(f"Score: {self.score}", True, WHITE)
        text_rect = score_text.get_rect(
            right=self.screen_width * self.scale_factor_x - margin,
            top=(10 + self.base_font_size) * self.scale_factor_y
        )
        self.game_surface.blit(score_text, text_rect)

    def draw_high_score(self):
        margin = 10 * self.scale_factor_x
        font_size = int(self.base_font_size * self.uniform_scale)
        game_font = pygame.font.SysFont("Arial", font_size)
        high_score_text = game_font.render(f"High Score: {self.high_score}", True, WHITE)
        text_rect = high_score_text.get_rect(
            right=self.screen_width * self.scale_factor_x - margin,
            top=(10 + self.base_font_size * 2) * self.scale_factor_y
        )
        self.game_surface.blit(high_score_text, text_rect)

    def play_death_animation(self):
        death_frames = 10
        for i in range(death_frames):
            self.game_surface.fill(RETRO_BG_COLOR)
            self.draw_walls()
            self.draw_enemies()
            self.draw_mjf_helper()
            self.draw_collectibles()
            self.update_particles()
            self.draw_power_up_status()
            self.draw_dopamine_bar()
            self.draw_lives()
            self.draw_level()
            self.draw_score()
            self.draw_high_score()

            # Draw player with death animation effect
            x = self.player_pos[0] * self.scale_factor_x
            y = self.player_pos[1] * self.scale_factor_y
            alpha = 255 - (i * (255 // death_frames))
            tinted_image = self.dopaman_image.copy()
            tinted_image.fill((255, 0, 0, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.game_surface.blit(tinted_image, (x - 20, y - 30))

            scaled_surface = pygame.transform.scale(self.game_surface, self.screen.get_size())
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(100)

    def levodopa_effect(self):
        self.dopamine_level = min(100, self.dopamine_level + 50)
        self.score += 50
        self.levodopa_active = True
        self.levodopa_timer = pygame.time.get_ticks()

    def dbs_effect(self):
        self.dopamine_level = min(100, self.dopamine_level + 70)
        self.tremor_active = False
        self.score += 70
        self.dbs_active = True
        self.dbs_timer = pygame.time.get_ticks()

    def stress_management_effect(self):
        self.dopamine_level = min(100, self.dopamine_level + 20)
        self.score += 20

    def mirapex_effect(self):
        for enemy in self.enemies:
            enemy.pos = [random.randint(0, self.screen_width), random.randint(0, self.screen_height)]
        self.score += 30

    def super_speed_effect(self):
        self.super_speed_active = True
        self.super_speed_timer = pygame.time.get_ticks()
        self.score += 40

    def shield_effect(self):
        self.shield_active = True
        self.shield_timer = pygame.time.get_ticks()
        self.score += 50

    def create_enemies(self):
        """Create enemies for the current level."""
        self.enemies = []
        
        # Set number of enemies per level
        if self.level == 1:
            num_enemies = 0
        elif self.level == 2:
            num_enemies = 1
        elif self.level == 3:
            num_enemies = 2
        else:
            num_enemies = 3

        enemy_types = [
            ("Depression", RED),
            ("Anxiety", YELLOW),
            ("Fatigue", ORANGE),
            ("Stress", PURPLE)
        ]

        for _ in range(num_enemies):
            # Select random enemy type
            enemy_name, enemy_color = random.choice(enemy_types)

            # Generate random position away from player
            while True:
                x = random.randint(50, self.screen_width - 50)
                y = random.randint(50, self.screen_height - 50)

                # Check distance from player
                dx = x - self.player_pos[0]
                dy = y - self.player_pos[1]
                distance = (dx * dx + dy * dy) ** 0.5

                if distance > 200:  # Minimum spawn distance from player
                    break

            # Create enemy with screen dimensions included
            enemy = Enemy(
                name=enemy_name,
                speed=self.enemy_speed,
                x=x,
                y=y,
                screen_width=self.screen_width,
                screen_height=self.screen_height
            )
            enemy.color = enemy_color  # Set the color attribute separately

            # Add enemy to list if it doesn't collide with walls
            if not self.check_wall_collision(enemy.rect):
                self.enemies.append(enemy)

    def setup_level(self, level):
        # ...existing code...
        
        # Add MJF helper after level 3
        if self.current_level >= 1:
            self.mjf_helper = MJFHelper((self.player.rect.x - 50, self.player.rect.y), self.player)
