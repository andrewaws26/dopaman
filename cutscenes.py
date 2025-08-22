import pygame
import sys
from typing import List, Optional, Tuple
from utils import render_text_wrapped, resource_path, WHITE, YELLOW, BLACK
from boss import Boss

# --- Constants ---
DIALOGUE_BOX_ALPHA = 180
FADE_MAX = 255
DIALOGUE_BOX_MARGIN = 50
DIALOGUE_BOX_HEIGHT = 100
PROMPT_Y_OFFSET = 80
IDLE_AMPLITUDE = 5
IDLE_SPEED = 0.1

# --- Helper Functions ---
def extract_frames(sprite_sheet: pygame.Surface, frame_width: int, frame_height: int, num_frames: int, row: int = 0) -> List[pygame.Surface]:
    """Extracts frames from a sprite sheet."""
    frames = []
    for col in range(num_frames):
        frame_rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
        frames.append(sprite_sheet.subsurface(frame_rect))
    return frames

def scale_surface(surface: pygame.Surface, size: Tuple[int, int]) -> pygame.Surface:
    """Scales a surface to the given size."""
    return pygame.transform.scale(surface, size)

def draw_fade(surface: pygame.Surface, color: Tuple[int, int, int], alpha: int):
    fade_surface = pygame.Surface(surface.get_size())
    fade_surface.set_alpha(alpha)
    fade_surface.fill(color)
    surface.blit(fade_surface, (0, 0))

def draw_dialogue_box(surface: pygame.Surface, text: str, font: pygame.font.Font, color: Tuple[int, int, int], screen: pygame.Surface):
    text_rect = pygame.Rect(DIALOGUE_BOX_MARGIN, screen.get_height() - DIALOGUE_BOX_HEIGHT - DIALOGUE_BOX_MARGIN, screen.get_width() - 2 * DIALOGUE_BOX_MARGIN, DIALOGUE_BOX_HEIGHT)
    text_background = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
    text_background.fill((0, 0, 0, DIALOGUE_BOX_ALPHA))
    surface.blit(text_background, text_rect.topleft)
    render_text_wrapped(surface, text, font, color, text_rect)

def load_and_scale_image(path: str, size: Tuple[int, int]) -> pygame.Surface:
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        return scale_surface(img, size)
    except pygame.error as e:
        print(f"Error loading image {path}: {e}")
        pygame.quit()
        sys.exit()

def draw_prompt(surface: pygame.Surface, text: str, font: pygame.font.Font, color: Tuple[int, int, int], screen: pygame.Surface, y_offset: int = PROMPT_Y_OFFSET):
    """Draws a prompt (e.g., 'Press Enter to continue...') centered at the bottom of the screen."""
    prompt_text = font.render(text, True, color)
    prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - y_offset))
    surface.blit(prompt_text, prompt_rect)

# --- Main Cutscene Functions ---
def show_level_story(
    game_surface: pygame.Surface,
    screen: pygame.Surface,
    level: int,
    EDUCATIONAL_CONTENT: dict,
    retro_font: pygame.font.Font,
    retro_small_font: pygame.font.Font,
    retro_bg_color: Tuple[int, int, int],
    player_image: pygame.Surface,
    mjf_helper_image: pygame.Surface,
    enemy_image: pygame.Surface
):
    """Handles the display of the story and cutscenes for each level."""
    fade_speed = 5
    dopaman_spritesheet = pygame.image.load(resource_path('images/dopaman.png')).convert_alpha()
    frame_cols = 8
    sheet_width, sheet_height = dopaman_spritesheet.get_size()
    frame_width = sheet_width // frame_cols
    frame_height = sheet_height
    dopaman_frames = extract_frames(dopaman_spritesheet, frame_width, frame_height, frame_cols, row=0)
    dopaman_scale_factor = 3
    dopaman_frames = [pygame.transform.scale(
        frame,
        (int(frame_width * dopaman_scale_factor), int(frame_height * dopaman_scale_factor))
    ) for frame in dopaman_frames]
    boss = None
    boss_scale_factor = 1
    if level == 2:
        dopaman_y = screen.get_height() // 2
        boss = Boss(
            resource_path("images/boss.png"),
            position=(screen.get_width() * 0.7, dopaman_y),
            scale_factor=4,
            frame_rows=1,
            frame_cols=50,
            animation_speed=50,
            flip=True
        )
        boss_scale_factor = 4
    if level == 1:
        show_cutscene(game_surface, screen, retro_small_font, retro_bg_color, dopaman_frames, fade_speed, level=1)
    elif level == 2:
        show_cutscene(game_surface, screen, retro_small_font, retro_bg_color, dopaman_frames, fade_speed, level=2, boss=boss, boss_scale_factor=boss_scale_factor)
    elif level == 3:
        show_cutscene_3(game_surface, screen, retro_small_font, retro_bg_color, dopaman_frames, fade_speed)
    elif level == 4:
        show_cutscene_4(game_surface, screen, retro_small_font, retro_bg_color, dopaman_frames, fade_speed)
    show_educational_content(game_surface, screen, level, EDUCATIONAL_CONTENT, retro_small_font, retro_bg_color, fade_speed)

def show_cutscene(game_surface, screen, retro_small_font, retro_bg_color, dopaman_frames, fade_speed, level, boss=None, boss_scale_factor=1):
    """Displays a cutscene for the given level."""
    clock = pygame.time.Clock()
    fade_alpha = FADE_MAX
    showing_cutscene = True
    dialogue_index = 0
    animation_timer = 0
    animation_interval = 100
    current_frame_index = 0
    screen_center_x = screen.get_width() // 2
    dopaman_pos = [screen_center_x, screen.get_height() // 2]
    dopaman_velocity = 2
    dopaman_direction = 1
    dopaman_move_range = screen.get_width() * 0.25
    dopaman_start_x = dopaman_pos[0]
    if level == 2 and boss is None:
        return
    dialogue = []
    background_layer = None
    if level == 1:
        dialogue = [
            "Dopaman: I am Dopaman, the guardian of balance in this bustling city.",
            "Without me, communication falters, and Neurocity falls into disarray."
        ]
        background_layer = load_and_scale_image('images/sjy.png', (screen.get_width(), screen.get_height()))
        middle_layer = load_and_scale_image('images/city.png', (screen.get_width(), screen.get_height()))
        foreground_layer = load_and_scale_image('images/illustration.png', (screen.get_width(), screen.get_height()))
    elif level == 2:
        dialogue = [
            "Dopaman: Something feels wrong... The CNS towers are damaged!",
            "Parkinon: Finally all the dopamine in Neurocity will be destoryed! Neurocity will crumble without you, Dopaman!",
            "Dopaman: Parkinon, my nemesis! How did you get here?! I must stabilize the towers before it's too late!",
            ""
        ]
        background_layer = load_and_scale_image('images/substantia_nigra_towers.png', (screen.get_width(), screen.get_height()))
    boss_jumping = False
    boss_jump_timer = 0
    JUMP_DURATION = 2000
    if level == 2:
        boss_jump = Boss(
            resource_path("images/boss-jump.png"),
            position=(screen.get_width() * 0.7, dopaman_pos[1]),
            scale_factor=4,
            frame_rows=1,
            frame_cols=12,
            animation_speed=40,
            flip=False
        )
    dopaman_chasing = False
    chase_speed = 8
    chase_jump_height = -400
    chase_jump_progress = 0
    chase_jump_duration = 2500
    original_dopaman_y = dopaman_pos[1]
    boss_offscreen = False
    # Fade-in at the start
    while fade_alpha > 0:
        game_surface.fill(retro_bg_color)
        if background_layer:
            game_surface.blit(background_layer, (0, 0))
            if level == 1:
                game_surface.blit(middle_layer, (0, 0))
                game_surface.blit(foreground_layer, (0, 0))
        dopaman_frame = dopaman_frames[0]
        game_surface.blit(
            dopaman_frame,
            (
                dopaman_pos[0] - dopaman_frame.get_width() // 2,
                dopaman_pos[1] - dopaman_frame.get_height() // 2
            )
        )
        draw_fade(game_surface, retro_bg_color, fade_alpha)
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
        fade_alpha = max(0, fade_alpha - fade_speed)
    fade_alpha = 0
    while showing_cutscene:
        dt = clock.tick(60)
        animation_timer += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if level == 2 and dialogue_index == len(dialogue) - 1:
                    if not boss.jumping:
                        boss = boss_jump
                        boss.start_jump()
                else:
                    dialogue_index += 1
                    if dialogue_index >= len(dialogue):
                        showing_cutscene = False
        game_surface.fill(retro_bg_color)
        if animation_timer >= animation_interval:
            current_frame_index = (current_frame_index + 1) % len(dopaman_frames)
            animation_timer = 0
        if background_layer:
            game_surface.blit(background_layer, (0, 0))
            if level == 1:
                game_surface.blit(middle_layer, (0, 0))
                game_surface.blit(foreground_layer, (0, 0))
        if level == 1:
            new_x = dopaman_pos[0] + (dopaman_velocity * dopaman_direction)
            if abs(new_x - screen_center_x) < dopaman_move_range:
                dopaman_pos[0] = new_x
            else:
                dopaman_direction *= -1
            dopaman_frame = dopaman_frames[current_frame_index]
            if dopaman_direction == -1:
                dopaman_frame = pygame.transform.flip(dopaman_frame, True, False)
        else:
            dopaman_frame = dopaman_frames[current_frame_index]
        game_surface.blit(
            dopaman_frame,
            (
                dopaman_pos[0] - dopaman_frame.get_width() // 2,
                dopaman_pos[1] - dopaman_frame.get_height() // 2
            )
        )
        if boss and level == 2:
            if dialogue_index >= len(dialogue) - 1:
                if not boss.jumping:
                    if boss.flip:
                        boss.flip = False
                        pygame.time.wait(300)
                    boss = boss_jump
                    boss.start_jump()
            jump_completed = boss.update(dt)
            boss.draw(game_surface, scale_factor=boss_scale_factor)
            if jump_completed:
                if boss.position[0] > screen.get_width() * 1.2:
                    boss_offscreen = True
            if boss_offscreen and not dopaman_chasing:
                dopaman_chasing = True
                chase_jump_progress = 0
            if dopaman_chasing:
                chase_jump_progress = min(chase_jump_progress + dt, chase_jump_duration)
                progress = chase_jump_progress / chase_jump_duration
                dopaman_pos[1] = original_dopaman_y + (chase_jump_height * progress * (1 - progress) * 4)
                dopaman_pos[0] += chase_speed
                dopaman_frame = dopaman_frames[current_frame_index]
            if boss_offscreen and dopaman_pos[0] > screen.get_width() * 1.2:
                showing_cutscene = False
        if dialogue_index < len(dialogue):
            draw_dialogue_box(game_surface, dialogue[dialogue_index], retro_small_font, WHITE, screen)
        if fade_alpha < FADE_MAX:
            fade_alpha = min(FADE_MAX, fade_alpha + fade_speed)
            draw_fade(game_surface, retro_bg_color, FADE_MAX - fade_alpha)
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
    # Fade-out at the end
    fade_alpha = 0
    while fade_alpha < FADE_MAX:
        game_surface.fill(retro_bg_color)
        if background_layer:
            game_surface.blit(background_layer, (0, 0))
            if level == 1:
                game_surface.blit(middle_layer, (0, 0))
                game_surface.blit(foreground_layer, (0, 0))
        game_surface.blit(
            dopaman_frame,
            (
                dopaman_pos[0] - dopaman_frame.get_width() // 2,
                dopaman_pos[1] - dopaman_frame.get_height() // 2
            )
        )
        if boss and level == 2:
            boss.draw(game_surface, scale_factor=boss_scale_factor)
        draw_fade(game_surface, retro_bg_color, fade_alpha)
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
        fade_alpha = min(FADE_MAX, fade_alpha + fade_speed)

def show_educational_content(
    game_surface: pygame.Surface,
    screen: pygame.Surface,
    level: int,
    EDUCATIONAL_CONTENT: dict,
    retro_small_font: pygame.font.Font,
    retro_bg_color: Tuple[int, int, int],
    fade_speed: int
):
    """Displays educational content related to the current level."""
    clock = pygame.time.Clock()
    fade_alpha = FADE_MAX
    educational_text = EDUCATIONAL_CONTENT.get(level, [])
    showing_education = True
    y_offset = 150
    text_rect = pygame.Rect(
        50, y_offset, screen.get_width() - 100, screen.get_height() - y_offset - 100
    )
    wrapped_lines = []
    words = " ".join(educational_text).split()
    line = ""
    for word in words:
        test_line = line + word + " "
        text_width, _ = retro_small_font.size(test_line)
        if text_width < text_rect.width:
            line = test_line
        else:
            wrapped_lines.append(line.strip())
            line = word + " "
    if line:
        wrapped_lines.append(line.strip())
    current_line_index = 0
    # Fade-in at the start
    while fade_alpha > 0:
        screen.fill(retro_bg_color)
        draw_fade(screen, retro_bg_color, fade_alpha)
        pygame.display.flip()
        fade_alpha = max(0, fade_alpha - fade_speed)
    fade_alpha = 0
    while showing_education:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                current_line_index += 1
                if current_line_index * (text_rect.height // (retro_small_font.get_linesize() + 10)) >= len(wrapped_lines):
                    showing_education = False
        screen.fill(retro_bg_color)
        line_height = retro_small_font.get_linesize() + 10
        current_y = text_rect.top
        for i in range(current_line_index * (text_rect.height // line_height), len(wrapped_lines)):
            line = wrapped_lines[i]
            if current_y + line_height > text_rect.bottom:
                break
            rendered_line = retro_small_font.render(line, True, WHITE)
            screen.blit(rendered_line, (text_rect.left, current_y))
            current_y += line_height
        draw_prompt(screen, "Press Enter to continue...", retro_small_font, YELLOW, screen)
        if fade_alpha < FADE_MAX:
            fade_alpha = min(FADE_MAX, fade_alpha + fade_speed)
            draw_fade(screen, retro_bg_color, FADE_MAX - fade_alpha)
        pygame.display.flip()
    # Fade-out at the end
    fade_alpha = 0
    while fade_alpha < FADE_MAX:
        screen.fill(retro_bg_color)
        draw_fade(screen, retro_bg_color, fade_alpha)
        pygame.display.flip()
        fade_alpha = min(FADE_MAX, fade_alpha + fade_speed)

def show_cutscene_3(game_surface: pygame.Surface, screen: pygame.Surface, retro_small_font: pygame.font.Font, retro_bg_color: Tuple[int, int, int], dopaman_frames: List[pygame.Surface], fade_speed: int):
    """Displays the third cutscene where MJF dramatically meets AssistDopman."""
    clock = pygame.time.Clock()
    fade_alpha = 0
    try:
        city_bg = load_and_scale_image('images/city-night.png', (screen.get_width(), screen.get_height()))
        sky_bg = load_and_scale_image('images/sky-night.png', (screen.get_width(), screen.get_height()))
        illustration = load_and_scale_image('images/illustration-night.png', (screen.get_width(), screen.get_height()))
        mjf_sprite = pygame.image.load(resource_path('images/mjf.jpeg')).convert_alpha()
    except Exception as e:
        print(f"Error loading assets: {e}")
        pygame.quit()
        sys.exit()
    camera_zoom = 1.0
    mjf_y = -mjf_sprite.get_height()  # Start MJF above the screen
    mjf_target_y = screen.get_height() // 2
    mjf_entry_speed = 8  # Speed of descent
    handshake_shown = False
    # PHASES: intro -> pre_entrance -> descent -> dialogue -> handshake
    scene_phase = "intro"
    dialogue = [
        "Dopaman: *sigh* Parkinon is getting too powerful I can't keep up...",
        "???: Need a hand with that neural network?",
        "Dopaman: Who's there?",
        "MJF: Micheal J. Fox. I've been battling Parkinon for years",
        "MJF: I've been watching your progress. Impressive, but you are missing two vital elements.",
        "Dopaman: What are they???",
        "MJF: The power of FAME and MONEY!",
        "MJF: Together, we could revolutionize Neurocity's rehabilitation protocols.",
        "Dopaman: I like the sound of that.",
        "MJF: I shall protect you from Parkinon's henchmen, Anxiety, Depression, and Fatigue.",
        "Dopaman: Let's go!!!"
    ]
    dialogue_index = 0
    dialogue_timer = 0
    showing_cutscene = True
    dopaman_animation_timer = 0
    dopaman_animation_interval = 100
    dopaman_frame_index = 0
    dopaman_idle_offset = 0
    dopaman_idle_direction = 1
    mjf_has_entered = False  # Track if MJF has finished his entrance
    # Fade-in at the start
    fade_alpha = FADE_MAX
    while fade_alpha > 0:
        game_surface.fill(retro_bg_color)
        game_surface.blit(sky_bg, (0, 0))
        game_surface.blit(city_bg, (0, 0))
        game_surface.blit(illustration, (0, 0))
        # Dopaman only for intro
        dopaman_frame = dopaman_frames[0]
        scaled_frame = pygame.transform.scale(
            dopaman_frame,
            (int(dopaman_frame.get_width() * camera_zoom), int(dopaman_frame.get_height() * camera_zoom))
        )
        game_surface.blit(scaled_frame, (screen.get_width()//2 - scaled_frame.get_width()//2, screen.get_height()//2 - scaled_frame.get_height()//2))
        draw_fade(game_surface, retro_bg_color, fade_alpha)
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
        fade_alpha = max(0, fade_alpha - fade_speed)
    # Start in pre_entrance phase
    scene_phase = "pre_entrance"
    while showing_cutscene:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if scene_phase == "pre_entrance":
                    dialogue_index += 1
                    # When we reach MJF's intro line, start descent
                    if dialogue_index == 3:
                        scene_phase = "descent"
                elif scene_phase == "descent":
                    # Only allow advancing after descent is finished
                    if mjf_has_entered:
                        scene_phase = "dialogue"
                        dialogue_index += 1  # Move to next line after MJF's entrance
                elif scene_phase == "dialogue":
                    dialogue_index += 1
                    if dialogue_index >= len(dialogue):
                        scene_phase = "handshake"
                elif scene_phase == "handshake":
                    showing_cutscene = False
        game_surface.fill(retro_bg_color)
        game_surface.blit(sky_bg, (0, 0))
        game_surface.blit(city_bg, (0, 0))
        game_surface.blit(illustration, (0, 0))
        if scene_phase == "intro":
            camera_zoom = min(camera_zoom + 0.01, 1.5)
            if camera_zoom >= 1.5:
                scene_phase = "pre_entrance"
        elif scene_phase == "pre_entrance":
            # Only show Dopaman and dialogue, not MJF
            pass
        elif scene_phase == "descent":
            # Animate MJF flying in from the top, show his line as he enters
            if mjf_y < mjf_target_y:
                mjf_y = min(mjf_y + mjf_entry_speed, mjf_target_y)
            else:
                mjf_has_entered = True
            # Always show MJF's intro line during descent
        elif scene_phase == "dialogue":
            mjf_y = mjf_target_y
        elif scene_phase == "handshake":
            camera_zoom = max(camera_zoom - 0.01, 1.0)
            if not handshake_shown:
                handshake_shown = True
        dopaman_animation_timer += dt
        if dopaman_animation_timer >= dopaman_animation_interval:
            dopaman_frame_index = (dopaman_frame_index + 1) % len(dopaman_frames)
            dopaman_animation_timer = 0
        dopaman_idle_offset += IDLE_SPEED * dopaman_idle_direction
        if abs(dopaman_idle_offset) > IDLE_AMPLITUDE:
            dopaman_idle_direction *= -1
        dopaman_frame = dopaman_frames[dopaman_frame_index]
        # Draw Dopaman
        if scene_phase == "intro":
            scaled_frame = pygame.transform.scale(
                dopaman_frame,
                (int(dopaman_frame.get_width() * camera_zoom), int(dopaman_frame.get_height() * camera_zoom))
            )
            game_surface.blit(scaled_frame, (screen.get_width()//2 - scaled_frame.get_width()//2, screen.get_height()//2 - scaled_frame.get_height()//2 + dopaman_idle_offset))
        else:
            game_surface.blit(dopaman_frame, (screen.get_width()//3, screen.get_height()//2 + dopaman_idle_offset))
        # Draw MJF: only during descent and after
        if scene_phase == "descent" or mjf_has_entered:
            game_surface.blit(mjf_sprite, (screen.get_width()*2//3, mjf_y))
        # Draw dialogue
        if scene_phase == "pre_entrance" and dialogue_index < len(dialogue):
            draw_dialogue_box(game_surface, dialogue[dialogue_index], retro_small_font, WHITE, screen)
        elif scene_phase == "descent":
            draw_dialogue_box(game_surface, dialogue[3], retro_small_font, WHITE, screen)
        elif scene_phase == "dialogue" and dialogue_index < len(dialogue):
            draw_dialogue_box(game_surface, dialogue[dialogue_index], retro_small_font, WHITE, screen)
        if fade_alpha < FADE_MAX:
            fade_alpha = min(FADE_MAX, fade_alpha + fade_speed)
            draw_fade(game_surface, retro_bg_color, FADE_MAX - fade_alpha)
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
    # Fade-out at the end
    fade_alpha = 0
    while fade_alpha < FADE_MAX:
        game_surface.fill(retro_bg_color)
        game_surface.blit(sky_bg, (0, 0))
        game_surface.blit(city_bg, (0, 0))
        game_surface.blit(illustration, (0, 0))
        # Draw Dopaman and MJF in their final positions
        game_surface.blit(dopaman_frame, (screen.get_width()//3, screen.get_height()//2 + dopaman_idle_offset))
        if mjf_has_entered:
            game_surface.blit(mjf_sprite, (screen.get_width()*2//3, mjf_y))
        draw_fade(game_surface, retro_bg_color, fade_alpha)
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
        fade_alpha = min(FADE_MAX, fade_alpha + fade_speed)

def show_cutscene_4(game_surface: pygame.Surface, screen: pygame.Surface, retro_small_font: pygame.font.Font, retro_bg_color: Tuple[int, int, int], dopaman_frames: List[pygame.Surface], fade_speed: int):
    """Displays the final cutscene where Dopaman and allies celebrate victory."""
    clock = pygame.time.Clock()
    fade_alpha = FADE_MAX
    animation_timer = 0
    animation_interval = 100
    current_frame_index = 0
    num_frames = len(dopaman_frames)
    dopaman_pos = [screen.get_width() // 2, screen.get_height() // 2]
    dopaman_velocity = 2
    dopaman_direction = 1
    dopaman_move_range = 50
    dopaman_start_x = dopaman_pos[0]
    dialogue = [
        "Dopaman: Neurocity shines once more, thanks to our efforts.",
        "Dopaman: We may never return to what we were,",
        "but together, we've proven that adaptation and resilience",
        "can overcome the greatest challenges."
    ]
    try:
        background_layer = load_and_scale_image('images/sjy.png', (screen.get_width(), screen.get_height()))
        middle_layer = load_and_scale_image('images/city.png', (screen.get_width(), screen.get_height()))
        foreground_layer = load_and_scale_image('images/illustration.png', (screen.get_width(), screen.get_height()))
    except Exception as e:
        print(f"Error loading images: {e}")
        pygame.quit()
        sys.exit()
    # Fade-in at the start
    while fade_alpha > 0:
        game_surface.fill(retro_bg_color)
        game_surface.blit(background_layer, (0, 0))
        game_surface.blit(middle_layer, (0, 0))
        game_surface.blit(foreground_layer, (0, 0))
        game_surface.blit(dopaman_frames[0], (dopaman_pos[0] - dopaman_frames[0].get_width() // 2, dopaman_pos[1] - dopaman_frames[0].get_height() // 2))
        draw_fade(game_surface, retro_bg_color, fade_alpha)
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
        fade_alpha = max(0, fade_alpha - fade_speed)
    showing_cutscene = True
    dialogue_index = 0
    dialogue_timer = 0
    dialogue_interval = 5000
    while showing_cutscene:
        dt = clock.tick(60)
        animation_timer += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_RETURN
                and dialogue_index >= len(dialogue)
            ):
                showing_cutscene = False
        if animation_timer >= animation_interval:
            current_frame_index = (current_frame_index + 1) % num_frames
            animation_timer = 0
        dopaman_pos[0] += dopaman_velocity * dopaman_direction
        if abs(dopaman_pos[0] - dopaman_start_x) > dopaman_move_range:
            dopaman_direction *= -1
        current_frame = dopaman_frames[current_frame_index]
        if dopaman_direction == -1:
            current_frame = pygame.transform.flip(current_frame, True, False)
        game_surface.blit(background_layer, (0, 0))
        game_surface.blit(middle_layer, (0, 0))
        game_surface.blit(foreground_layer, (0, 0))
        game_surface.blit(
            current_frame,
            (
                dopaman_pos[0] - current_frame.get_width() // 2,
                dopaman_pos[1] - current_frame.get_height() // 2
            )
        )
        if dialogue_index < len(dialogue):
            draw_dialogue_box(game_surface, dialogue[dialogue_index], retro_small_font, WHITE, screen)
            dialogue_timer += dt
            if dialogue_timer >= dialogue_interval:
                dialogue_index += 1
                dialogue_timer = 0
        else:
            draw_prompt(game_surface, "Press Enter to continue...", retro_small_font, YELLOW, screen, y_offset=50)
        if fade_alpha < FADE_MAX:
            fade_alpha = min(FADE_MAX, fade_alpha + fade_speed)
            draw_fade(game_surface, retro_bg_color, FADE_MAX - fade_alpha)
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
    # Fade-out at the end
    fade_alpha = 0
    while fade_alpha < FADE_MAX:
        game_surface.fill(retro_bg_color)
        game_surface.blit(background_layer, (0, 0))
        game_surface.blit(middle_layer, (0, 0))
        game_surface.blit(foreground_layer, (0, 0))
        game_surface.blit(current_frame, (dopaman_pos[0] - current_frame.get_width() // 2, dopaman_pos[1] - current_frame.get_height() // 2))
        draw_fade(game_surface, retro_bg_color, fade_alpha)
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
        fade_alpha = min(FADE_MAX, fade_alpha + fade_speed)

if __name__ == "__main__":
    import argparse
    import os
    # Initialize mixer BEFORE pygame.init()
    try:
        pygame.mixer.pre_init(44100, -16, 2, 512)
    except Exception as e:
        print(f"Warning: mixer pre_init failed: {e}")
    pygame.init()
    print(f"Mixer initialized: {pygame.mixer.get_init()}")
    parser = argparse.ArgumentParser(description="Test Dopaman cutscenes.")
    parser.add_argument("--cutscene", type=int, default=1, help="Cutscene number: 1, 2, 3, or 4")
    args = parser.parse_args()

    # Set up window
    screen_size = (960, 720)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Cutscene Test")
    game_surface = pygame.Surface(screen_size)
    retro_bg_color = (20, 20, 40)

    # Dummy EDUCATIONAL_CONTENT
    EDUCATIONAL_CONTENT = {
        1: ["Dopamine is a neurotransmitter that helps control movement and coordination."],
        2: ["Parkinson's disease is caused by the loss of dopamine-producing neurons."],
        3: ["Fame and money can help raise awareness and fund research for Parkinson's."],
        4: ["Adaptation and resilience are key to overcoming challenges in life."]
    }

    # Load a font (fallback to default if not found)
    try:
        retro_small_font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 18)
        retro_font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 32)
    except Exception:
        retro_small_font = pygame.font.SysFont(None, 18)
        retro_font = pygame.font.SysFont(None, 32)

    # Dummy images for player, mjf_helper, enemy
    dummy_img = pygame.Surface((32, 32), pygame.SRCALPHA)
    dummy_img.fill((255, 255, 255, 128))

    # Try to load real Dopaman frames
    try:
        dopaman_spritesheet = pygame.image.load(resource_path('images/dopaman.png')).convert_alpha()
        frame_cols = 8
        sheet_width, sheet_height = dopaman_spritesheet.get_size()
        frame_width = sheet_width // frame_cols
        frame_height = sheet_height
        dopaman_frames = extract_frames(dopaman_spritesheet, frame_width, frame_height, frame_cols, row=0)
        dopaman_scale_factor = 3
        dopaman_frames = [pygame.transform.scale(
            frame,
            (int(frame_width * dopaman_scale_factor), int(frame_height * dopaman_scale_factor))
        ) for frame in dopaman_frames]
    except Exception as e:
        print("Warning: Could not load real Dopaman sprite, using dummy.")
        dopaman_frames = [dummy_img] * 8

    # Initialize mixer and play music for the selected cutscene
    music_files = {
        1: "sounds/background_music.mp3",
        2: "sounds/background_music.mp3",
        3: "sounds/background_music.mp3",
        4: "sounds/background_music.mp3"
    }
    try:
        music_file = music_files.get(args.cutscene)
        resolved_path = resource_path(music_file) if music_file else None
        print(f"Resolved music file: {resolved_path}")
        if resolved_path and os.path.exists(resolved_path):
            pygame.mixer.music.load(resolved_path)
            pygame.mixer.music.play(-1)
            print("Music started.")
        else:
            print(f"Music file not found: {resolved_path}")
    except Exception as e:
        print(f"Warning: Could not play music: {e}")

    # Play the selected cutscene with real frames
    if args.cutscene == 1:
        show_cutscene(game_surface, screen, retro_small_font, retro_bg_color, dopaman_frames, 8, level=1)
    elif args.cutscene == 2:
        show_cutscene(game_surface, screen, retro_small_font, retro_bg_color, dopaman_frames, 8, level=2)
    elif args.cutscene == 3:
        show_cutscene_3(game_surface, screen, retro_small_font, retro_bg_color, dopaman_frames, 8)
    elif args.cutscene == 4:
        show_cutscene_4(game_surface, screen, retro_small_font, retro_bg_color, dopaman_frames, 8)
    else:
        print("Invalid cutscene number. Use 1, 2, 3, or 4.")

    # Stop music at the end
    try:
        pygame.mixer.music.stop()
        # Give the mixer a moment to flush audio before quitting (test harness only)
        pygame.time.wait(500)
    except Exception:
        pass
    pygame.quit()
