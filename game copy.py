import pygame
import sys
import random
import os
from PIL import Image, ImageDraw
from story_animation import show_level_story
from utils import resource_path

# Check if required assets exist, if not, create placeholders
if not os.path.exists(resource_path("dopaman.png")):
    # Create Dopaman image
    width, height = 40, 60
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    # Draw a simple head (circle)
    draw.ellipse((10, 0, 30, 20), fill=(255, 223, 186, 255))  # Skin color
    # Draw eyes
    draw.ellipse((15, 5, 17, 7), fill=(0, 0, 0, 255))  # Left eye
    draw.ellipse((23, 5, 25, 7), fill=(0, 0, 0, 255))  # Right eye
    # Draw a simple body (rectangle)
    draw.rectangle((10, 20, 30, 50), fill=(0, 0, 255, 255))  # Blue shirt
    # Draw legs (two rectangles)
    draw.rectangle((10, 50, 18, 60), fill=(0, 0, 0, 255))  # Left leg
    draw.rectangle((22, 50, 30, 60), fill=(0, 0, 0, 255))  # Right leg
    # Save the image as a PNG
    image.save(resource_path("dopaman.png"))

if not os.path.exists(resource_path("mjf.png")):  # Change from mjfpic.jpeg to mjf.png
    # Create Michael J. Fox image
    width, height = 40, 60
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    # Draw a simple head (circle)
    draw.ellipse((10, 0, 30, 20), fill=(255, 223, 186, 255))
    draw.rectangle((10, 20, 30, 50), fill=(128, 128, 128, 255))
    draw.rectangle((10, 50, 18, 60), fill=(0, 0, 0, 255))
    draw.rectangle((22, 50, 30, 60), fill=(0, 0, 0, 255))
    draw.text((12, 25), "MJF", fill=(255, 255, 255, 255))
    image.save(resource_path("mjf.png"))  # Save as PNG instead of JPEG

if not os.path.exists(resource_path("PressStart2P.ttf")):
    # Provide instructions to download the font
    print("Please download 'PressStart2P.ttf' font file and place it in the same directory as this script.")
    sys.exit()

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize mixer for sound

# Load and play background music
try:
    pygame.mixer.music.load(resource_path("background_music.mp3"))  # Can also use .wav or .ogg files
    pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
    pygame.mixer.music.play(-1)  # -1 means loop indefinitely
except:
    print("Warning: Could not load background music file. Continuing without music.")

# Check if sound files exist
if os.path.exists(resource_path("background_music.ogg")):
    background_music = pygame.mixer.Sound(resource_path("background_music.ogg"))
    background_music.play(-1)  # Loop indefinitely
else:
    background_music = None
    print("Warning: 'background_music.ogg' not found. Continuing without background music.")

if os.path.exists(resource_path("collect_sound.mp3")):
    collect_sound = pygame.mixer.Sound(resource_path("collect_sound.mp3"))
else:
    collect_sound = None
    print("Warning: 'collect_sound.mp3' not found. Collect sound will be silent.")

if os.path.exists(resource_path("enemy_hit.wav")):
    enemy_hit_sound = pygame.mixer.Sound(resource_path("enemy_hit.wav"))
else:
    enemy_hit_sound = None
    print("Warning: 'enemy_hit.wav' not found. Enemy hit sound will be silent.")

# Load game over sound
if os.path.exists(resource_path("game_over.mp3")):
    game_over_sound = pygame.mixer.Sound(resource_path("game_over.mp3"))
else:
    game_over_sound = None
    print("Warning: 'game_over.mp3' not found. Game over sound will be silent.")

# Create a sounds dictionary
sounds = {
    'collect': collect_sound,
    'enemy_hit': enemy_hit_sound,
    'game_over': game_over_sound
}

# Set up display dimensions
screen_width, screen_height = 800, 600
window_size = (screen_width, screen_height)
scale_factor_x = 1
scale_factor_y = 1

# Get monitor info for fullscreen
info = pygame.display.Info()
monitor_size = (info.current_w, info.current_h)
is_fullscreen = False

# Create the game surface
game_surface = pygame.Surface((screen_width, screen_height))

def toggle_fullscreen():
    global screen, is_fullscreen
    if is_fullscreen:
        screen = pygame.display.set_mode(window_size)
        is_fullscreen = False
    else:
        screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
        is_fullscreen = True

screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Dopaman")

# Set up colors
pink = (255, 182, 193)
blue = (0, 0, 255)
red = (255, 0, 0)
black = (0, 0, 0)
green = (0, 255, 0)
yellow = (255, 255, 0)
purple = (128, 0, 128)
orange = (255, 165, 0)
brown = (139, 69, 19)
white = (255, 255, 255)
dark_gray = (169, 169, 169)
cyan = (0, 255, 255)
retro_bg_color = (0, 0, 0)

# Load fonts
retro_font = pygame.font.Font(resource_path("PressStart2P.ttf"), 32)
retro_small_font = pygame.font.Font(resource_path("PressStart2P.ttf"), 16)
game_font = pygame.font.SysFont("Arial", 28)

# Load player image
player_image = pygame.image.load(resource_path("dopaman.png"))
player_image = pygame.transform.scale(player_image, (40, 60))

# Load Michael J. Fox helper image
mjf_helper_image = pygame.image.load(resource_path("mjf.png"))  # Update image loading to use PNG
mjf_helper_image = pygame.transform.scale(mjf_helper_image, (40, 60))

# Load enemy image
enemy_image = pygame.image.load(resource_path("enemy.png"))
enemy_image = pygame.transform.scale(enemy_image, (40, 60))

# Game variables
dopamine_level = 100
dopamine_depletion_rate = 0.05
initial_player_speed = 5
reduced_speed = 3
level = 1
lives = 3
score = 0

player_speed = initial_player_speed

# High score
try:
    with open(resource_path('high_score.txt'), 'r') as f:
        high_score = int(f.read())
except:
    high_score = 0

# Difficulty settings
difficulty_settings = {
    "Easy": {"depletion_rate": 0.04, "enemy_speed": 1.0},
    "Medium": {"depletion_rate": 0.05, "enemy_speed": 1.5},
    "Hard": {"depletion_rate": 0.06, "enemy_speed": 2.0}
}

selected_difficulty = "Medium"
enemy_speed = difficulty_settings[selected_difficulty]["enemy_speed"]
dopamine_depletion_rate = difficulty_settings[selected_difficulty]["depletion_rate"]

# Game state
game_running = True
game_paused = False
player_pos = [screen_width // 2, screen_height // 2]
damage_animation_active = False
damage_animation_timer = 0
damage_animation_duration = 1000
damage_flash_interval = 100
confused_active = False
confused_timer = 0

# Walls (rectangles)
walls = []

def generate_walls():
    walls.clear()
    num_walls = min(3, level)
    for _ in range(num_walls):
        while True:
            wall_width = random.randint(100, 300)
            wall_height = random.randint(20, 30)
            wall_x = random.randint(0, screen_width - wall_width)
            wall_y = random.randint(0, screen_height - wall_height)
            new_wall = pygame.Rect(wall_x, wall_y, wall_width, wall_height)
            if not new_wall.colliderect(pygame.Rect(player_pos[0] - 20, player_pos[1] - 30, 40, 60)):
                walls.append(new_wall)
                break

generate_walls()

# Function to draw walls
def draw_walls():
    for wall in walls:
        pygame.draw.rect(game_surface, dark_gray, wall)

# Function to check collision with walls
def check_wall_collision(rect):
    scaled_rect = pygame.Rect(
        rect.x * scale_factor_x,
        rect.y * scale_factor_y,
        rect.width * scale_factor_x,
        rect.height * scale_factor_y
    )
    for wall in walls:
        scaled_wall = pygame.Rect(
            wall.x * scale_factor_x,
            wall.y * scale_factor_y,
            wall.width * scale_factor_x,
            wall.height * scale_factor_y
        )
        if scaled_rect.colliderect(scaled_wall):
            return True
    return False

# Enemy classes
class Enemy:
    def __init__(self, name, speed, effect):
        self.name = name
        self.speed = speed
        self.effect = effect
        self.pos = [random.randint(0, screen_width), random.randint(0, screen_height)]

    def move(self):
        if self.name == "Depression":  # New enemy type
            # Moves unpredictably
            self.pos[0] += random.choice([-1, 1]) * self.speed
            self.pos[1] += random.choice([-1, 1]) * self.speed
        else:
            # ...existing movement code...
            pass

    @property
    def rect(self):
        # Return the rectangle for collision detection
        return pygame.Rect(self.pos[0] - 20, self.pos[1] - 20, 40, 40)

enemies = []

def create_enemies():
    enemies.clear()
    if level >= 3:
        enemies.append(Enemy("Stress", enemy_speed, "normal"))
    if level >= 5:
        enemies.append(Enemy("Anxiety", enemy_speed + 0.2, "slow_player"))
    if level >= 7:
        enemies.append(Enemy("Fatigue", enemy_speed + 0.1, "reduce_dopamine"))
    if level >= 9:
        enemies.append(Enemy("Depression", enemy_speed + 0.3, "confuse_player"))

create_enemies()

# Michael J. Fox helper introduced at level 5
mjf_helper_speed = 2.0  # Changed from _helper_speed
mjf_helper_pos = [random.randint(0, screen_width), random.randint(0, screen_height)]
mjf_helper_radius = 100  # Changed from _helper_radius

# Collectibles
num_collectibles = {
    "dopamine": 2,
    "medicine": 1,
    "levodopa": 1,
    "dbs": 1,
    "stress_management": 2,
    "mirapex": 1,
    "super_speed": 1,
    "shield": 1
}

# Initialize all collectibles lists at the top
dopamine_collectibles = []
medicine_collectibles = []
levodopa_collectibles = []
dbs_collectibles = []
stress_management_collectibles = []
mirapex_collectibles = []
super_speed_collectibles = []
shield_collectibles = []

# Function to generate collectible positions without overlap and not on walls
def generate_collectibles(num, exclusion_zone, exclusion_radius):
    collectibles = []
    max_attempts = 1000
    attempt = 0
    collectible_radius = 15  # Assuming collectibles are drawn with a radius of 15

    while len(collectibles) < num and attempt < max_attempts:
        x = random.randint(collectible_radius, screen_width - collectible_radius)
        y = random.randint(collectible_radius, screen_height - collectible_radius)
        collectible_rect = pygame.Rect(x - collectible_radius, y - collectible_radius, collectible_radius * 2, collectible_radius * 2)
        
        # Check exclusion zone
        if exclusion_zone and ((x - exclusion_zone[0]) ** 2 + (y - exclusion_zone[1]) ** 2) ** 0.5 < exclusion_radius:
            attempt += 1
            continue
        
        # Check wall collisions
        wall_collision = False
        for wall in walls:
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
    
    if attempt >= max_attempts:
        print(f"Warning: Could not place all collectibles after {max_attempts} attempts")
    
    return collectibles

dopamine_collectibles = generate_collectibles(num_collectibles["dopamine"], player_pos, 50)
medicine_collectibles = generate_collectibles(num_collectibles["medicine"], player_pos, 50)
levodopa_collectibles = generate_collectibles(num_collectibles["levodopa"], player_pos, 50)
dbs_collectibles = generate_collectibles(num_collectibles["dbs"], player_pos, 50)
tremor_active = False
super_speed_active = False
super_speed_timer = 0
levodopa_active = False
levodopa_timer = 0
dbs_active = False
dbs_timer = 0
shield_active = False
shield_timer = 0

particles = []

# Power-up effects
def levodopa_effect():
    global dopamine_level, score, levodopa_active, levodopa_timer
    dopamine_level = min(100, dopamine_level + 50)
    score += 50
    levodopa_active = True
    levodopa_timer = pygame.time.get_ticks()

def dbs_effect():
    global dopamine_level, tremor_active, score, dbs_active, dbs_timer
    dopamine_level = min(100, dopamine_level + 70)
    tremor_active = False
    score += 70
    dbs_active = True
    dbs_timer = pygame.time.get_ticks()

def stress_management_effect():
    global dopamine_level, score
    dopamine_level = min(100, dopamine_level + 20)
    score += 20

def mirapex_effect():
    global enemies, score
    for enemy in enemies:
        enemy.pos = [random.randint(0, screen_width), random.randint(0, screen_height)]
    score += 30

def super_speed_effect():
    global super_speed_active, super_speed_timer, score
    super_speed_active = True
    super_speed_timer = pygame.time.get_ticks()
    score += 40

def shield_effect():
    global shield_active, shield_timer, score
    shield_active = True
    shield_timer = pygame.time.get_ticks()
    score += 50

def create_particles(position, color):
    for _ in range(10):
        particles.append([[position[0], position[1]], [random.uniform(-1, 1), random.uniform(-1, 1)], random.randint(2, 4), color])

def update_particles():
    for particle in particles[:]:
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2] -= 0.1
        if particle[2] <= 0:
            particles.remove(particle)
        else:
            pygame.draw.circle(game_surface, particle[3], (int(particle[0][0]), int(particle[0][1])), int(particle[2]))

def scale_pos(x, y):
    """Helper function to scale coordinates"""
    return (int(x * scale_factor_x), int(y * scale_factor_y))

def scale_rect(rect):
    """Helper function to scale rectangles"""
    return pygame.Rect(
        rect.x * scale_factor_x,
        rect.y * scale_factor_y,
        rect.width * scale_factor_x,
        rect.height * scale_factor_y
    )

def draw_dopamine_bar():
    bar_width = dopamine_level * 3
    pygame.draw.rect(game_surface, blue, (50, 20, bar_width, 30))
    dopamine_text = game_font.render(f"Dopamine Level: {int(dopamine_level)}%", True, white)
    game_surface.blit(dopamine_text, (50, 60))

def draw_lives():
    lives_text = game_font.render(f"Lives: {lives}", True, white)
    game_surface.blit(lives_text, (screen_width - 150, 20))

def draw_level():
    level_text = game_font.render(f"Level: {level}", True, white)
    game_surface.blit(level_text, (screen_width // 2 - 50, 20))

def draw_score():
    score_text = game_font.render(f"Score: {score}", True, white)
    game_surface.blit(score_text, (screen_width - 150, 60))

def draw_high_score():
    high_score_text = game_font.render(f"High Score: {high_score}", True, white)
    game_surface.blit(high_score_text, (screen_width - 200, 100))

def draw_player():
    x = player_pos[0]
    y = player_pos[1]
    if shield_active:
        tinted_image = player_image.copy()
        tinted_image.fill((0, 255, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)
        game_surface.blit(tinted_image, (x - 20, y - 30))
        pygame.draw.circle(game_surface, cyan, (x, y), 40, 2)
    else:
        game_surface.blit(player_image, (x - 20, y - 30))

def draw_enemies():
    for enemy in enemies:
        label = game_font.render(enemy.name, True, red)
        game_surface.blit(label, (enemy.pos[0] - label.get_width() // 2, enemy.pos[1] - 20))

def draw_mjf_helper():
    if level >= 5:
        game_surface.blit(mjf_helper_image, (mjf_helper_pos[0] - 20, mjf_helper_pos[1] - 30))
        label = game_font.render("Michael J. Fox", True, yellow)
        game_surface.blit(label, (mjf_helper_pos[0] - label.get_width() // 2, mjf_helper_pos[1] - 50))

def draw_collectibles():
    for collectible in dopamine_collectibles[:]:
        pygame.draw.circle(game_surface, green, collectible, 15)
        label = game_font.render("Dopamine", True, white)
        game_surface.blit(label, (collectible[0] - label.get_width() // 2, collectible[1] - 25))
    for medicine in medicine_collectibles[:]:
        pygame.draw.circle(game_surface, yellow, medicine, 15)
        label = game_font.render("Medicine", True, white)
        game_surface.blit(label, (medicine[0] - label.get_width() // 2, medicine[1] - 25))
    for levodopa in levodopa_collectibles[:]:
        pygame.draw.circle(game_surface, purple, levodopa, 15)
        label = game_font.render("Levodopa", True, white)
        game_surface.blit(label, (levodopa[0] - label.get_width() // 2, levodopa[1] - 25))
    for dbs in dbs_collectibles[:]:
        pygame.draw.circle(game_surface, orange, dbs, 15)
        label = game_font.render("DBS", True, white)
        game_surface.blit(label, (dbs[0] - label.get_width() // 2, dbs[1] - 25))
    for stress in stress_management_collectibles[:]:
        pygame.draw.circle(game_surface, brown, stress, 15)
        label = game_font.render("Stress Mgmt", True, white)
        game_surface.blit(label, (stress[0] - label.get_width() // 2, stress[1] - 25))
    for mirapex in mirapex_collectibles[:]:
        pygame.draw.circle(game_surface, blue, mirapex, 15)
        label = game_font.render("Mirapex", True, white)
        game_surface.blit(label, (mirapex[0] - label.get_width() // 2, mirapex[1] - 25))
    for speed in super_speed_collectibles[:]:
        pygame.draw.circle(game_surface, cyan, speed, 15)
        label = game_font.render("Super Speed", True, white)
        game_surface.blit(label, (speed[0] - label.get_width() // 2, speed[1] - 25))
    for shield in shield_collectibles[:]:
        pygame.draw.circle(game_surface, white, shield, 15)
        label = game_font.render("Shield", True, red)  # Changed color to red
        game_surface.blit(label, (shield[0] - label.get_width() // 2, shield[1] - 25))

def draw_power_up_status():
    x_offset = 50
    y_offset = screen_height - 40
    if super_speed_active:
        remaining_time = max(0, (5000 - (pygame.time.get_ticks() - super_speed_timer)) // 1000)
        label = game_font.render(f"Super Speed: {remaining_time}s", True, cyan)
        game_surface.blit(label, (x_offset, y_offset))
        x_offset += label.get_width() + 20
    if shield_active:
        remaining_time = max(0, (5000 - (pygame.time.get_ticks() - shield_timer)) // 1000)
        label = game_font.render(f"Shield: {remaining_time}s", True, red)
        game_surface.blit(label, (x_offset, y_offset))
        x_offset += label.get_width() + 20
    # ...add other power-ups as needed...

def check_collectible_collision():
    global dopamine_level, tremor_active, score
    scaled_player_rect = scale_rect(pygame.Rect(player_pos[0] - 20, player_pos[1] - 30, 40, 60))
    for collectible in dopamine_collectibles[:]:
        if scaled_player_rect.collidepoint(scale_pos(collectible[0], collectible[1])):
            dopamine_collectibles.remove(collectible)
            dopamine_level = min(100, dopamine_level + 20)
            score += 20
            create_particles(collectible, green)
            if collect_sound:
                collect_sound.play()

    for medicine in medicine_collectibles[:]:
        if scaled_player_rect.collidepoint(scale_pos(medicine[0], medicine[1])):
            medicine_collectibles.remove(medicine)
            dopamine_level = min(100, dopamine_level + 30)
            tremor_active = False
            score += 30
            create_particles(medicine, yellow)
            if collect_sound:
                collect_sound.play()

    for levodopa in levodopa_collectibles[:]:
        if scaled_player_rect.collidepoint(scale_pos(levodopa[0], levodopa[1])):
            levodopa_collectibles.remove(levodopa)
            levodopa_effect()
            create_particles(levodopa, purple)
            if collect_sound:
                collect_sound.play()

    for dbs in dbs_collectibles[:]:
        if scaled_player_rect.collidepoint(scale_pos(dbs[0], dbs[1])):
            dbs_collectibles.remove(dbs)
            dbs_effect()
            create_particles(dbs, orange)
            if collect_sound:
                collect_sound.play()

    for stress in stress_management_collectibles[:]:
        if scaled_player_rect.collidepoint(scale_pos(stress[0], stress[1])):
            stress_management_collectibles.remove(stress)
            stress_management_effect()
            create_particles(stress, brown)
            if collect_sound:
                collect_sound.play()

    for mirapex in mirapex_collectibles[:]:
        if scaled_player_rect.collidepoint(scale_pos(mirapex[0], mirapex[1])):
            mirapex_collectibles.remove(mirapex)
            mirapex_effect()
            create_particles(mirapex, blue)
            if collect_sound:
                collect_sound.play()

    for speed in super_speed_collectibles[:]:
        if scaled_player_rect.collidepoint(scale_pos(speed[0], speed[1])):
            super_speed_collectibles.remove(speed)
            super_speed_effect()
            if collect_sound:
                collect_sound.play()  # Play sound effect
            create_particles(speed, cyan)

    for shield in shield_collectibles[:]:
        if scaled_player_rect.collidepoint(scale_pos(shield[0], shield[1])):
            shield_collectibles.remove(shield)
            shield_effect()
            if collect_sound:
                collect_sound.play()  # Play sound effect
            create_particles(shield, white)

def apply_movement():
    global tremor_active, confused_active
    keys = pygame.key.get_pressed()
    speed = reduced_speed if dopamine_level < 40 else player_speed

    if super_speed_active:
        speed *= 1.5

    # Determine movement direction
    if confused_active:
        x_direction = keys[pygame.K_LEFT] - keys[pygame.K_RIGHT]
        y_direction = keys[pygame.K_UP] - keys[pygame.K_DOWN]
    else:
        x_direction = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        y_direction = keys[pygame.K_DOWN] - keys[pygame.K_UP]

    # Calculate proposed new position
    new_x = player_pos[0] + x_direction * speed
    new_y = player_pos[1] + y_direction * speed

    # Create a rectangle for the player's new position
    new_rect = pygame.Rect(new_x - 20, new_y - 30, 40, 60)

    # Check for collisions with walls
    if not check_wall_collision(new_rect):
        # Update player position only if no collision
        if 0 <= new_rect.left and new_rect.right <= screen_width:  # Horizontal boundaries
            player_pos[0] = new_x
        if 0 <= new_rect.top and new_rect.bottom <= screen_height:  # Vertical boundaries
            player_pos[1] = new_y

    # Apply tremor effect if dopamine level is low and DBS is inactive
    if not dbs_active:
        tremor_active = dopamine_level < 30
    if tremor_active:
        player_pos[0] += random.choice([-1, 1])
        player_pos[1] += random.choice([-1, 1])


def move_enemies():
    for enemy in enemies:
        new_x, new_y = enemy.pos[0], enemy.pos[1]

        if enemy.pos[0] < player_pos[0]:
            new_x += enemy.speed
        elif enemy.pos[0] > player_pos[0]:
            new_x -= enemy.speed

        if enemy.pos[1] < player_pos[1]:
            new_y += enemy.speed
        elif enemy.pos[1] > player_pos[1]:
            new_y -= enemy.speed

        new_rect = pygame.Rect(new_x - 20, new_y - 20, 40, 40)

        if not check_wall_collision(new_rect) and 0 <= new_rect.left <= screen_width and 0 <= new_rect.top <= screen_height:
            enemy.pos[0], enemy.pos[1] = new_x, new_y

def move_mjf_helper():
    global dopamine_level
    if level >= 5:
        new_x, new_y = mjf_helper_pos[0], mjf_helper_pos[1]

        if mjf_helper_pos[0] < player_pos[0]:
            new_x += mjf_helper_speed
        elif mjf_helper_pos[0] > player_pos[0]:
            new_x -= mjf_helper_speed

        if mjf_helper_pos[1] < player_pos[1]:
            new_y += mjf_helper_speed
        elif mjf_helper_pos[1] > player_pos[1]:
            new_y -= mjf_helper_speed

        if 0 <= new_x - 20 and new_x + 20 <= screen_width and 0 <= new_y - 30 and new_y + 30 <= screen_height:
            mjf_helper_pos[0], mjf_helper_pos[1] = new_x, new_y

        if abs(mjf_helper_pos[0] - player_pos[0]) < mjf_helper_radius and abs(mjf_helper_pos[1] - player_pos[1]) < mjf_helper_radius:
            dopamine_level = min(100, dopamine_level + 0.5)

def check_game_over(sounds=None):
    global lives, game_running, high_score, tremor_active, confused_active, shield_active

    player_rect = pygame.Rect(player_pos[0] - 20, player_pos[1] - 30, 40, 60)
    collision_occurred = False

    for enemy in enemies:
        enemy_rect = pygame.Rect(enemy.pos[0] - 20, enemy.pos[1] - 20, 40, 40)
        if player_rect.colliderect(enemy_rect):
            if not shield_active:
                lives -= 1
                create_particles(player_pos, red)
                collision_occurred = True
                if enemy_hit_sound:
                    enemy_hit_sound.play()
                play_death_animation()

                if lives <= 0:
                    game_over(sounds)
                else:
                    # Reset player position and state
                    player_pos[0], player_pos[1] = screen_width // 2, screen_height // 2
                    tremor_active = False
                    confused_active = False
                    shield_active = False

                    # Reset enemy positions
                    for enemy in enemies:
                        enemy.pos = [random.randint(0, screen_width), random.randint(0, screen_height)]

    if collision_occurred and lives <= 0:
        # Save high score
        if score > high_score:
            high_score = score
            try:
                with open('high_score.txt', 'w') as f:
                    f.write(str(high_score))
            except:
                print("Could not save high score")

        # End game
        game_running = False


def apply_enemy_effects(sounds):
    global dopamine_level, score, game_running, confused_active, confused_timer

    # Define the player's rectangle for collision detection
    player_rect = pygame.Rect(player_pos[0] - 20, player_pos[1] - 30, 40, 60)

    # Iterate through all enemies and check collisions
    for enemy in enemies:
        if player_rect.colliderect(enemy.rect):
            # Apply the effect based on the enemy type
            if enemy.name == "Depression":
                dopamine_level -= dopamine_depletion_rate
                if sounds.get('enemy_hit'):
                    sounds['enemy_hit'].play()
                if dopamine_level <= 0:
                    game_running = False
                    return
            elif enemy.name == "Anxiety":
                player_speed = reduced_speed
            elif enemy.name == "Fatigue":
                dopamine_level -= 0.5  # Additional depletion
            elif enemy.name == "Stress":
                confused_active = True
                confused_timer = pygame.time.get_ticks()


class Star:
    def __init__(self):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.speed = random.uniform(1, 3)
        self.size = random.randint(1, 3)

    def move(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = screen_width
            self.y = random.randint(0, screen_height)
            self.speed = random.uniform(1, 3)
            self.size = random.randint(1, 3)

def tutorial_screen():
    clock = pygame.time.Clock()
    showing_tutorial = True
    while showing_tutorial:
        game_surface.fill(retro_bg_color)
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
        y_offset = 100
        for line in tutorial_text:
            text_surface = game_font.render(line, True, white)
            text_rect = text_surface.get_rect(center=(screen_width // 2, y_offset))
            game_surface.blit(text_surface, text_rect)
            y_offset += 40

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    showing_tutorial = False

def difficulty_selection():
    global selected_difficulty, enemy_speed, dopamine_depletion_rate
    clock = pygame.time.Clock()
    selecting = True
    difficulties = ["Easy", "Medium", "Hard"]
    selected_index = 1
    while selecting:
        game_surface.fill(retro_bg_color)
        title_text = retro_font.render("SELECT DIFFICULTY", True, green)
        title_rect = title_text.get_rect(center=(screen_width // 2, 100))
        game_surface.blit(title_text, title_rect)

        y_offset = 200
        for i, diff in enumerate(difficulties):
            if i == selected_index:
                diff_text = retro_small_font.render(f"> {diff}", True, yellow)
            else:
                diff_text = retro_small_font.render(diff, True, white)
            diff_rect = diff_text.get_rect(center=(screen_width // 2, y_offset))
            game_surface.blit(diff_text, diff_rect)  # Corrected line
            y_offset += 50

        instruction_text = retro_small_font.render("Use UP/DOWN arrows and ENTER to select", True, white)
        instruction_rect = instruction_text.get_rect(center=(screen_width // 2, screen_height - 100))
        game_surface.blit(instruction_text, instruction_rect)

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(difficulties)
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(difficulties)
                if event.key == pygame.K_RETURN:
                    selected_difficulty = difficulties[selected_index]
                    enemy_speed = difficulty_settings[selected_difficulty]["enemy_speed"]
                    dopamine_depletion_rate = difficulty_settings[selected_difficulty]["depletion_rate"]
                    selecting = False

def show_prologue():
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
    y_offset = 100
    for line in story_text:
        text_surface = retro_small_font.render(line, True, white)
        text_rect = text_surface.get_rect(center=(screen_width // 2, y_offset))
        text_surfaces.append(text_surface)
        text_positions.append(text_rect)
        y_offset += 30

    while showing_prologue:
        game_surface.fill(retro_bg_color)

        # Draw text with fade effect
        for surface, pos in zip(text_surfaces, text_positions):
            temp_surface = surface.copy()
            temp_surface.set_alpha(fade_alpha)
            game_surface.blit(temp_surface, pos)

        # Fade in
        if fade_alpha < 255:
            fade_alpha = min(255, fade_alpha + fade_speed)

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    showing_prologue = False
                if event.key == pygame.K_f:  # Changed from K_F10
                    toggle_fullscreen()

def start_screen():
    show_prologue()  # Add this line at the start of the function
    clock = pygame.time.Clock()
    blink = True
    blink_timer = 0

    stars = [Star() for _ in range(100)]

    while True:
        game_surface.fill(retro_bg_color)

        for star in stars:
            star.move()
            pygame.draw.circle(game_surface, white, (int(star.x), int(star.y)), star.size)

        title_text = retro_font.render("DOPAMAN", True, green)
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 3))  # Fixed method name
        game_surface.blit(title_text, title_rect)

        if blink:
            instruction_text = retro_small_font.render("Press Enter to Start", True, white)
            instruction_rect = instruction_text.get_rect(center=(screen_width // 2, screen_height // 2))  # Fixed method name
            game_surface.blit(instruction_text, instruction_rect)

        high_score_text = retro_small_font.render(f'HIGH SCORE: {high_score}', True, white)
        high_score_rect = high_score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        game_surface.blit(high_score_text, high_score_rect)

        blink_timer += clock.get_time()
        if blink_timer >= 500:
            blink = not blink
            blink_timer = 0

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    difficulty_selection()
                    tutorial_screen()
                    return
                if event.key == pygame.K_f:  # Changed from K_F10
                    toggle_fullscreen()

def pause_screen():
    paused = True
    clock = pygame.time.Clock()
    pygame.mixer.music.pause()  # Pause music when game is paused
    while paused:
        game_surface.fill(retro_bg_color)
        pause_text = retro_font.render("PAUSED", True, yellow)
        pause_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2))
        game_surface.blit(pause_text, pause_rect)
        instruction_text = retro_small_font.render("Press 'P' to Resume", True, white)
        instruction_rect = instruction_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        game_surface.blit(instruction_text, instruction_rect)
        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pygame.mixer.music.unpause()  # Unpause music when game resumes
                    paused = False
                if event.key == pygame.K_f:  # Changed from K_F10
                    toggle_fullscreen()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def game_over(sounds=None):  # Add sounds parameter with default None
    pygame.mixer.music.stop()  # Stop background music
    global game_running, score, high_score
    game_running = False
    
    # Play game over sound if available
    if sounds and sounds.get('game_over'):
        sounds['game_over'].play()
    
    clock = pygame.time.Clock()
    game_over_displayed = True
    while game_over_displayed:
        game_surface.fill(retro_bg_color)
        game_over_text = retro_font.render("GAME OVER", True, red)
        game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 3))
        game_surface.blit(game_over_text, game_over_rect)

        score_text = game_font.render(f"Score: {score}", True, white)
        score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2))
        game_surface.blit(score_text, score_rect)

        high_score_text = game_font.render(f"High Score: {high_score}", True, white)
        high_score_rect = high_score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        game_surface.blit(high_score_text, high_score_rect)

        instruction_text = retro_small_font.render("Press Enter to Restart or Esc to Quit", True, white)
        instruction_rect = instruction_text.get_rect(center=(screen_width // 2, screen_height - 100))
        game_surface.blit(instruction_text, instruction_rect)

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_over_displayed = False
                    restart_game()
                    game_running = True  # Set game_running to True to restart the game
                elif event.key == pygame.K_ESCAPE:
                    game_over_displayed = False
                    game_running = False  # Set game_running to False to exit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def restart_game():
    pygame.mixer.music.play(-1)  # Restart music when game restarts
    global dopamine_level, level, lives, score, player_speed, dopamine_depletion_rate, player_pos, tremor_active, game_running
    dopamine_level = 100
    level = 1
    lives = 3
    score = 0
    tremor_active = False
    player_speed = initial_player_speed
    player_pos = [screen_width // 2, screen_height // 2]
    generate_walls()
    create_enemies()
    game_running = True  # Set game_running to True to restart the game loop

def check_level_complete():
    # Check if all collectible lists are empty
    return (len(dopamine_collectibles) == 0 and
            len(medicine_collectibles) == 0 and
            len(levodopa_collectibles) == 0 and
            len(dbs_collectibles) == 0 and
            len(stress_management_collectibles) == 0 and
            len(mirapex_collectibles) == 0 and
            len(super_speed_collectibles) == 0 and
            len(shield_collectibles) == 0)

# Add this near the top with other global variables
EDUCATIONAL_CONTENT = {
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

# Add this new function


# Modify the next_level function
def next_level():
    global level, dopamine_depletion_rate, player_speed, dopamine_collectibles, medicine_collectibles
    global levodopa_collectibles, stress_management_collectibles, dbs_collectibles, mirapex_collectibles
    global super_speed_collectibles, shield_collectibles, mjf_helper_pos, score, enemy_speed

    # Display the story for the new level
    show_level_story(
        game_surface,
        screen,
        level,
        EDUCATIONAL_CONTENT,
        retro_font,
        retro_small_font,
        retro_bg_color,
        player_image,
        mjf_helper_image,
        enemy_image
    )

    # Adjust game variables based on the new level
    enemy_speed *= 1.05
    player_speed = initial_player_speed * (1.02 ** (level - 1))
    score += 100

    # Generate walls for the new level
    generate_walls()
    
    # Generate collectibles after walls are created
    dopamine_collectibles = generate_collectibles(num_collectibles["dopamine"], player_pos, 50)
    medicine_collectibles = generate_collectibles(num_collectibles["medicine"], player_pos, 50)
    levodopa_collectibles = generate_collectibles(num_collectibles["levodopa"], player_pos, 50)
    dbs_collectibles = generate_collectibles(num_collectibles["dbs"], player_pos, 50)
    stress_management_collectibles = generate_collectibles(num_collectibles["stress_management"], player_pos, 50)
    mirapex_collectibles = generate_collectibles(num_collectibles["mirapex"], player_pos, 50)
    super_speed_collectibles = generate_collectibles(num_collectibles["super_speed"], player_pos, 50)
    shield_collectibles = generate_collectibles(num_collectibles["shield"], player_pos, 50)
    
    # Set Michael J. Fox helper position
    mjf_helper_pos = [random.randint(0, screen_width), random.randint(0, screen_height)]
    
    # Create enemies for the new level
    create_enemies()

def start_game(sounds=None):
    global game_running, game_paused, level
    global levodopa_active, dbs_active, tremor_active, shield_active, super_speed_active, dopamine_level
    global confused_active, confused_timer
    confused_active = False
    confused_timer = 0
    game_running = True  # Ensure game_running is True at the start
    level = 1  # Start at level 1

    # Show the story for the first level (cutscene 1)
    next_level()  # This will show cutscene 1

    clock = pygame.time.Clock()
    while game_running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause_screen()
                if event.key == pygame.K_f:
                    toggle_fullscreen()
        
        # Update game state
        apply_movement()
        move_enemies()
        move_mjf_helper()
        check_collectible_collision()
        apply_enemy_effects(sounds)
        check_game_over(sounds)
        if dopamine_level <= 0:
            game_over(sounds)
        
        # Draw everything
        game_surface.fill(retro_bg_color)
        draw_walls()
        draw_enemies()
        draw_mjf_helper()
        draw_collectibles()
        draw_player()
        update_particles()
        draw_power_up_status()
        draw_dopamine_bar()
        draw_lives()
        draw_level()
        draw_score()
        draw_high_score()
        
        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        
        # Deplete dopamine
        dopamine_level -= dopamine_depletion_rate
        
        # Handle power-up timers
        if super_speed_active and pygame.time.get_ticks() - super_speed_timer > 5000:
            super_speed_active = False
        if shield_active and pygame.time.get_ticks() - shield_timer > 5000:
            shield_active = False
        if confused_active and pygame.time.get_ticks() - confused_timer > 5000:
            confused_active = False
        
        # Check if level is complete
        if check_level_complete():
            level += 1
            next_level()
            continue

def play_death_animation():
    death_frames = 10
    for i in range(death_frames):
        game_surface.fill(retro_bg_color)
        draw_walls()
        draw_enemies()
        draw_mjf_helper()
        draw_collectibles()
        update_particles()
        draw_power_up_status()
        draw_dopamine_bar()
        draw_lives()
        draw_level()
        draw_score()
        draw_high_score()

        # Draw player with death animation effect
        x = player_pos[0]
        y = player_pos[1]
        alpha = 255 - (i * (255 // death_frames))
        tinted_image = player_image.copy()
        tinted_image.fill((255, 0, 0, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        game_surface.blit(tinted_image, (x - 20, y - 30))

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(100)

# Main execution
while True:
    start_screen()
    start_game(sounds)

pygame.quit()
sys.exit()
