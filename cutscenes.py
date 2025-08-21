import pygame
import sys
from utils import render_text_wrapped, resource_path, WHITE, YELLOW, BLACK
from boss import Boss

def extract_frames(sprite_sheet, frame_width, frame_height, num_frames, row=0):
    frames = []
    for col in range(num_frames):
        frame_rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
        frames.append(sprite_sheet.subsurface(frame_rect))
    return frames

def show_level_story(
    game_surface, screen, level, EDUCATIONAL_CONTENT, retro_font, retro_small_font, retro_bg_color,
    player_image, mjf_helper_image, enemy_image
):
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
        dopaman_y = screen.get_height() // 2  # Get Dopaman's Y position
        boss = Boss(
            resource_path("images/boss.png"),
            position=(screen.get_width() * 0.7, dopaman_y),  # Set boss Y to match Dopaman
            scale_factor=4,
            frame_rows=1,
            frame_cols=50,
            animation_speed=50,  # Faster animation speed
            flip=True  # Flip the boss to face Dopaman
        )
        boss_scale_factor = 4  # Increased scale factor
    
    # Show the appropriate cutscene based on level
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
    clock = pygame.time.Clock()
    fade_alpha = 0
    showing_cutscene = True
    dialogue_index = 0

    # Animation variables
    animation_timer = 0
    animation_interval = 100  # Time between frames (ms)
    current_frame_index = 0  # Current frame index for Dopaman animation

    # Dopaman's position and movement
    screen_center_x = screen.get_width() // 2
    dopaman_pos = [screen_center_x, screen.get_height() // 2]  # Start at center
    dopaman_velocity = 2  # Reduced speed
    dopaman_direction = 1
    dopaman_move_range = screen.get_width() * 0.25  # 25% of screen width for movement
    dopaman_start_x = dopaman_pos[0]  # Center point for back-and-forth movement

    # Remove the boss re-initialization since it's already initialized correctly
    if level == 2 and boss is None:
        return  # Boss should be initialized by show_level_story

    # Background and dialogue setup for each level
    dialogue = []  # Initialize dialogue as an empty list to avoid UnboundLocalError
    background_layer = None  # Default to None to handle undefined levels gracefully

    if level == 1:
        dialogue = [
            "Dopaman: I am Dopaman, the guardian of balance in this bustling city.",
            "Without me, communication falters, and Neurocity falls into disarray."
        ]
        background_layer = pygame.image.load(resource_path('images/sjy.png')).convert()
        middle_layer = pygame.image.load(resource_path('images/city.png')).convert_alpha()
        foreground_layer = pygame.image.load(resource_path('images/illustration.png')).convert_alpha()
        
        background_layer = pygame.transform.scale(background_layer, (screen.get_width(), screen.get_height()))
        middle_layer = pygame.transform.scale(middle_layer, (screen.get_width(), screen.get_height()))
        foreground_layer = pygame.transform.scale(foreground_layer, (screen.get_width(), screen.get_height()))
    elif level == 2:
        dialogue = [
            "Dopaman: Something feels wrong... The CNS towers are damaged!",
            "Parkinon: Finally all the dopamine in Neurocity will be destoryed! Neurocity will crumble without you, Dopaman!",
            "Dopaman: Parkinon, my nemesis! How did you get here?! I must stabilize the towers before it's too late!",
            ""  # Add empty dialogue to prevent auto-exit
        ]
        background_layer = pygame.image.load(resource_path('images/substantia_nigra_towers.png')).convert()
        background_layer = pygame.transform.scale(background_layer, (screen.get_width(), screen.get_height()))

    # Add boss jump variables
    boss_jumping = False
    boss_jump_timer = 0
    JUMP_DURATION = 2000  # 2 seconds for full jump animation
    
    if level == 2:
        # Load boss jump spritesheet
        boss_jump = Boss(
            resource_path("images/boss-jump.png"),
            position=(screen.get_width() * 0.7, dopaman_pos[1]),
            scale_factor=4,
            frame_rows=1,
            frame_cols=12,
            animation_speed=40,  # Even faster animation for jump
            flip=False  # Boss should face right when jumping
        )

    # Add chase variables for level 2
    dopaman_chasing = False
    chase_speed = 8  # Faster speed to catch up
    chase_jump_height = -400  # Higher jump
    chase_jump_progress = 0
    chase_jump_duration = 2500  # 2.5 seconds
    original_dopaman_y = dopaman_pos[1]
    boss_offscreen = False
    
    while showing_cutscene:
        dt = clock.tick(60)  # Control frame rate
        animation_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if level == 2 and dialogue_index == len(dialogue) - 1:
                    # Only prevent advancement for level 2's last (empty) dialogue
                    if not boss.jumping:
                        boss = boss_jump
                        boss.start_jump()
                else:
                    dialogue_index += 1
                    if dialogue_index >= len(dialogue):
                        showing_cutscene = False

        # Clear the game surface
        game_surface.fill(retro_bg_color)

        # Update Dopaman animation frame
        if animation_timer >= animation_interval:
            current_frame_index = (current_frame_index + 1) % len(dopaman_frames)
            animation_timer = 0

        # Draw background
        if background_layer:
            game_surface.blit(background_layer, (0, 0))
            if level == 1:  # Add middle and foreground layers for level 1
                game_surface.blit(middle_layer, (0, 0))
                game_surface.blit(foreground_layer, (0, 0))

        # Update Dopaman's position for level 1 patrol movement
        if level == 1:
            # Keep Dopaman within the safe range
            new_x = dopaman_pos[0] + (dopaman_velocity * dopaman_direction)
            if abs(new_x - screen_center_x) < dopaman_move_range:
                dopaman_pos[0] = new_x
            else:
                dopaman_direction *= -1  # Reverse direction at boundaries

            # Flip Dopaman's sprite based on direction
            dopaman_frame = dopaman_frames[current_frame_index]
            if dopaman_direction == -1:
                dopaman_frame = pygame.transform.flip(dopaman_frame, True, False)
        else:
            dopaman_frame = dopaman_frames[current_frame_index]

        # Draw Dopaman
        game_surface.blit(
            dopaman_frame,
            (
                dopaman_pos[0] - dopaman_frame.get_width() // 2,
                dopaman_pos[1] - dopaman_frame.get_height() // 2
            )
        )

        # Update and draw boss for level 2
        if boss and level == 2:
            if dialogue_index >= len(dialogue) - 1:
                if not boss.jumping:
                    if boss.flip:  # If boss is still facing left
                        # Turn animation - brief pause before jumping
                        boss.flip = False  # Turn to face right
                        pygame.time.wait(300)  # Brief pause to show the turn
                    boss = boss_jump
                    boss.start_jump()
            
            # Always update boss animation regardless of jumping state
            jump_completed = boss.update(dt)
            boss.draw(game_surface, scale_factor=boss_scale_factor)
            
            # Check if boss is offscreen
            if jump_completed:
                # Only check for offscreen after jump is complete
                if boss.position[0] > screen.get_width() * 1.2:
                    boss_offscreen = True
            
            # Start Dopaman's chase only after boss is offscreen
            if boss_offscreen and not dopaman_chasing:
                dopaman_chasing = True
                chase_jump_progress = 0
            
            # Update Dopaman's chase movement
            if dopaman_chasing:
                chase_jump_progress = min(chase_jump_progress + dt, chase_jump_duration)
                progress = chase_jump_progress / chase_jump_duration
                
                # Parabolic jump motion for Dopaman
                dopaman_pos[1] = original_dopaman_y + (chase_jump_height * progress * (1 - progress) * 4)
                dopaman_pos[0] += chase_speed  # Move right
                
                # Keep Dopaman facing right during chase
                dopaman_frame = dopaman_frames[current_frame_index]
            
            # End scene after both characters are offscreen
            if boss_offscreen and dopaman_pos[0] > screen.get_width() * 1.2:
                showing_cutscene = False

        # Draw dialogue box
        if dialogue_index < len(dialogue):
            text_rect = pygame.Rect(50, screen.get_height() - 150, screen.get_width() - 100, 100)
            text_background = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
            text_background.fill((0, 0, 0, 180))  # Semi-transparent black
            game_surface.blit(text_background, text_rect.topleft)
            render_text_wrapped(game_surface, dialogue[dialogue_index], retro_small_font, WHITE, text_rect)

        # Fade-in effect
        if fade_alpha < 255:
            fade_alpha = min(255, fade_alpha + fade_speed)
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.set_alpha(255 - fade_alpha)
            fade_surface.fill(retro_bg_color)
            game_surface.blit(fade_surface, (0, 0))

        # Update the display
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()

def show_educational_content(
    game_surface,
    screen,
    level,
    EDUCATIONAL_CONTENT,
    retro_small_font,
    retro_bg_color,
    fade_speed
):
    """
    Displays educational content related to the current level.
    """
    clock = pygame.time.Clock()
    fade_alpha = 0
    educational_text = EDUCATIONAL_CONTENT.get(level, [])
    showing_education = True

    # Define a rectangle for the text area that is adjusted to the screen size
    y_offset = 150
    text_rect = pygame.Rect(
        50, y_offset, screen.get_width() - 100, screen.get_height() - y_offset - 100
    )

    # Prepare wrapped lines of educational content
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

    # Ensure game_surface matches the screen size to avoid scaling issues
    game_surface = pygame.Surface(screen.get_size())

    while showing_education:
        dt = clock.tick(60)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                current_line_index += 1
                if current_line_index * (text_rect.height // (retro_small_font.get_linesize() + 10)) >= len(wrapped_lines):
                    showing_education = False

        # Fill the screen with the background color
        screen.fill(retro_bg_color)

        # Draw educational content line by line with spacing
        line_height = retro_small_font.get_linesize() + 10
        current_y = text_rect.top

        for i in range(current_line_index * (text_rect.height // line_height), len(wrapped_lines)):
            line = wrapped_lines[i]
            if current_y + line_height > text_rect.bottom:
                break  # Stop rendering if text goes beyond the allowed space
            rendered_line = retro_small_font.render(line, True, WHITE)
            screen.blit(rendered_line, (text_rect.left, current_y))
            current_y += line_height

        # Draw continue prompt
        prompt_text = retro_small_font.render("Press Enter to continue...", True, YELLOW)
        prompt_rect = prompt_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - 80)
        )
        screen.blit(prompt_text, prompt_rect)

        # Fade-in effect
        if fade_alpha < 255:
            fade_alpha = min(255, fade_alpha + fade_speed)
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.set_alpha(255 - fade_alpha)
            fade_surface.fill(retro_bg_color)
            screen.blit(fade_surface, (0, 0))

        # Update the display
        pygame.display.flip()

# Cutscene 3: Rallying Allies (After Level 3)
def show_cutscene_3(game_surface, screen, retro_small_font, retro_bg_color, dopaman_frames, fade_speed):
    """
    Displays the third cutscene where MJF dramatically meets AssistDopman.
    """
    clock = pygame.time.Clock()
    fade_alpha = 0
    
    # Load additional assets
    try:
        # Update image paths to use night-themed versions
        city_bg = pygame.image.load(resource_path('images/city-night.png')).convert_alpha()
        sky_bg = pygame.image.load(resource_path('images/sky-night.png')).convert_alpha()
        illustration = pygame.image.load(resource_path('images/illustration-night.png')).convert_alpha()
        mjf_sprite = pygame.image.load(resource_path('images/mjf.jpeg')).convert_alpha()
        
        # Scale all background images
        city_bg = pygame.transform.scale(city_bg, (screen.get_width(), screen.get_height()))
        sky_bg = pygame.transform.scale(sky_bg, (screen.get_width(), screen.get_height()))
        illustration = pygame.transform.scale(illustration, (screen.get_width(), screen.get_height()))

    except pygame.error as e:
        print(f"Error loading assets: {e}")
        pygame.quit()
        sys.exit()

    # Camera and animation variables
    camera_zoom = 1.0
    mjf_y = -100  # Start MJF above screen
    handshake_shown = False
    scene_phase = "intro"  # intro, descent, dialogue, handshake
    
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

    # Add animation timer for Dopaman
    dopaman_animation_timer = 0
    dopaman_animation_interval = 100
    dopaman_frame_index = 0
    dopaman_idle_offset = 0
    dopaman_idle_direction = 1
    IDLE_AMPLITUDE = 5  # Pixels to move up/down while idle
    IDLE_SPEED = 0.1    # Speed of idle animation

    while showing_cutscene:
        dt = clock.tick(60)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if scene_phase == "dialogue":
                    dialogue_index += 1
                    if dialogue_index >= len(dialogue):
                        scene_phase = "handshake"
                elif scene_phase == "handshake":
                    showing_cutscene = False

        # Clear screen
        game_surface.fill(retro_bg_color)
        
        # Draw background layers in correct order
        game_surface.blit(sky_bg, (0, 0))      # Sky first
        game_surface.blit(city_bg, (0, 0))     # City second
        game_surface.blit(illustration, (0, 0)) # Illustration on top

        # Scene phase logic
        if scene_phase == "intro":
            camera_zoom = min(camera_zoom + 0.01, 1.5)
            if camera_zoom >= 1.5:
                scene_phase = "descent"

        elif scene_phase == "descent":
            mjf_y += 2
            if mjf_y >= screen.get_height() // 2:
                scene_phase = "dialogue"

        elif scene_phase == "dialogue":
            mjf_y = screen.get_height() // 2
            
        elif scene_phase == "handshake":
            # Zoom out for final shot
            camera_zoom = max(camera_zoom - 0.01, 1.0)
            if not handshake_shown:
                handshake_shown = True

        # Update Dopaman's idle animation
        dopaman_animation_timer += dt
        if dopaman_animation_timer >= dopaman_animation_interval:
            dopaman_frame_index = (dopaman_frame_index + 1) % len(dopaman_frames)
            dopaman_animation_timer = 0
        
        # Add slight floating motion
        dopaman_idle_offset += IDLE_SPEED * dopaman_idle_direction
        if abs(dopaman_idle_offset) > IDLE_AMPLITUDE:
            dopaman_idle_direction *= -1

        # Draw characters
        dopaman_frame = dopaman_frames[dopaman_frame_index]
        if scene_phase == "intro":
            # Draw zoomed in frustrated AssistDopman
            scaled_frame = pygame.transform.scale(
                dopaman_frame,
                (int(dopaman_frame.get_width() * camera_zoom),
                 int(dopaman_frame.get_height() * camera_zoom))
            )
            game_surface.blit(scaled_frame, 
                (screen.get_width()//2 - scaled_frame.get_width()//2,
                 screen.get_height()//2 - scaled_frame.get_height()//2 + dopaman_idle_offset))
        else:
            # Draw normal sized AssistDopman with idle animation
            game_surface.blit(dopaman_frame, 
                (screen.get_width()//3,
                 screen.get_height()//2 + dopaman_idle_offset))

        # Draw MJF
        if scene_phase != "intro":
            game_surface.blit(mjf_sprite, (screen.get_width()*2//3, mjf_y))

        # Draw dialogue
        if scene_phase == "dialogue" and dialogue_index < len(dialogue):
            text_rect = pygame.Rect(50, screen.get_height() - 150, screen.get_width() - 100, 100)
            text_background = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
            text_background.fill((0, 0, 0, 180))
            game_surface.blit(text_background, text_rect.topleft)
            render_text_wrapped(game_surface, dialogue[dialogue_index], retro_small_font, WHITE, text_rect)

        # Fade effect
        if fade_alpha < 255:
            fade_alpha = min(255, fade_alpha + fade_speed)
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.set_alpha(255 - fade_alpha)
            fade_surface.fill(retro_bg_color)
            game_surface.blit(fade_surface, (0, 0))

        # Update display
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()

# Cutscene 4: Victory and Realism (After Final Level)
def show_cutscene_4(game_surface, screen, retro_small_font, retro_bg_color, dopaman_frames, fade_speed):
    """
    Displays the final cutscene where Dopaman and allies celebrate victory.
    """
    clock = pygame.time.Clock()
    fade_alpha = 0  # Alpha value for the fade-in effect

    # Animation variables
    animation_timer = 0
    animation_interval = 100
    current_frame_index = 0
    num_frames = len(dopaman_frames)

    # Movement variables for Dopaman
    dopaman_pos = [screen.get_width() // 2, screen.get_height() // 2]
    dopaman_velocity = 2
    dopaman_direction = 1
    dopaman_move_range = 50
    dopaman_start_x = dopaman_pos[0]

    # Dialogue lines for the cutscene
    dialogue = [
        "Dopaman: Neurocity shines once more, thanks to our efforts.",
        "Dopaman: We may never return to what we were,",
        "but together, we've proven that adaptation and resilience",
        "can overcome the greatest challenges."
    ]

    # Load the layered background images (same as Cutscene 1)
    try:
        background_layer = pygame.image.load(resource_path('images/sjy.png')).convert()
        middle_layer = pygame.image.load(resource_path('images/city.png')).convert_alpha()
        foreground_layer = pygame.image.load(resource_path('images/illustration.png')).convert_alpha()
    except pygame.error as e:
        print(f"Error loading images: {e}")
        pygame.quit()
        sys.exit()

    # Scale the background layers to fit the screen
    background_layer = pygame.transform.scale(background_layer, (screen.get_width(), screen.get_height()))
    middle_layer = pygame.transform.scale(middle_layer, (screen.get_width(), screen.get_height()))
    foreground_layer = pygame.transform.scale(foreground_layer, (screen.get_width(), screen.get_height()))

    # Ensure game_surface matches the screen size to avoid scaling issues
    game_surface = pygame.Surface(screen.get_size())

    # Variables to control the cutscene loop
    showing_cutscene = True
    dialogue_index = 0
    dialogue_timer = 0
    dialogue_interval = 5000

    # Main loop for Cutscene 4
    while showing_cutscene:
        dt = clock.tick(60)
        animation_timer += dt

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Check if Enter key is pressed to proceed
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_RETURN
                and dialogue_index >= len(dialogue)
            ):
                showing_cutscene = False

        # Update animation frame
        if animation_timer >= animation_interval:
            current_frame_index = (current_frame_index + 1) % num_frames
            animation_timer = 0

        # Update Dopaman's position
        dopaman_pos[0] += dopaman_velocity * dopaman_direction
        if abs(dopaman_pos[0] - dopaman_start_x) > dopaman_move_range:
            dopaman_direction *= -1  # Change direction

        # Flip Dopaman's image based on movement direction
        current_frame = dopaman_frames[current_frame_index]
        if dopaman_direction == -1:
            current_frame = pygame.transform.flip(current_frame, True, False)

        # Render the background layers in order (parallax effect)
        game_surface.blit(background_layer, (0, 0))  # Farthest back
        game_surface.blit(middle_layer, (0, 0))      # Middle layer
        game_surface.blit(foreground_layer, (0, 0))  # Closest layer

        # Draw Dopaman
        game_surface.blit(
            current_frame,
            (
                dopaman_pos[0] - current_frame.get_width() // 2,
                dopaman_pos[1] - current_frame.get_height() // 2
            )
        )

        # Display dialogue
        if dialogue_index < len(dialogue):
            text_rect = pygame.Rect(50, screen.get_height() - 150, screen.get_width() - 100, 100)
            text_background = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
            text_background.fill((0, 0, 0, 180))
            game_surface.blit(text_background, text_rect.topleft)
            render_text_wrapped(game_surface, dialogue[dialogue_index], retro_small_font, WHITE, text_rect)
            dialogue_timer += dt
            if dialogue_timer >= dialogue_interval:
                dialogue_index += 1
                dialogue_timer = 0
        else:
            prompt_text = retro_small_font.render("Press Enter to continue...", True, YELLOW)
            prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            game_surface.blit(prompt_text, prompt_rect)

        # Fade-in effect
        if fade_alpha < 255:
            fade_alpha = min(255, fade_alpha + fade_speed)
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.set_alpha(255 - fade_alpha)
            fade_surface.fill(retro_bg_color)
            game_surface.blit(fade_surface, (0, 0))

        # Update the display
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()

# Function to display information about an ally when clicked
def show_ally_info(game_surface, screen, retro_small_font, ally_index, retro_bg_color, fade_speed):
    """
    Displays information about an ally character when clicked.
    """
    # Information texts for each ally
    info_texts = [
        ["Medication (Levodopa):", "Increases dopamine levels to improve motor control."],
        ["Deep Brain Stimulation:", "Electrical impulses reduce symptoms like tremors."],
        ["Exercise:", "Enhances mobility and overall brain health."]
    ]
    clock = pygame.time.Clock()
    fade_alpha = 0
    showing_info = True

    # Prepare the text to display
    info_text = "\n".join(info_texts[ally_index])

    # Define text area
    y_offset = 150
    text_rect = pygame.Rect(50, y_offset, screen.get_width() - 100, screen.get_height() - y_offset - 100)

    # Ensure game_surface matches the screen size to avoid scaling issues
    game_surface = pygame.Surface(screen.get_size())

    while showing_info:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Check if Enter key is pressed to return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                showing_info = False

        game_surface.fill(retro_bg_color)

        # Draw the ally information text
        render_text_wrapped(game_surface, info_text, retro_small_font, WHITE, text_rect)

        # Draw continue prompt
        prompt_text = retro_small_font.render("Press Enter to return...", True, YELLOW)
        prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
        game_surface.blit(prompt_text, prompt_rect)

        # Fade-in effect
        if fade_alpha < 255:
            fade_alpha = min(255, fade_alpha + fade_speed)
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.set_alpha(255 - fade_alpha)
            fade_surface.fill(retro_bg_color)
            game_surface.blit(fade_surface, (0, 0))

        # Update the display
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
