import pygame
import sys
from utils import resource_path

# Initialize Pygame
pygame.init()

# Constants for colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

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

def show_level_story(
    game_surface, screen, level, EDUCATIONAL_CONTENT, retro_font, retro_small_font, retro_bg_color,
    player_image, mjf_helper_image, enemy_image
):
    fade_speed = 5

    # Determine which cutscene to display based on the level
    if level == 1:
        show_cutscene_1(game_surface, screen, retro_small_font, retro_bg_color, player_image, fade_speed)
    elif level == 2:
        show_cutscene_2(game_surface, screen, retro_small_font, retro_bg_color, player_image, enemy_image, fade_speed)
    elif level == 3:
        show_cutscene_3(game_surface, screen, retro_small_font, retro_bg_color, player_image, mjf_helper_image, fade_speed)
    elif level == 4:
        show_cutscene_4(game_surface, screen, retro_small_font, retro_bg_color, player_image, fade_speed)
    else:
        # For levels without specific cutscenes, show educational content
        show_educational_content(game_surface, screen, level, EDUCATIONAL_CONTENT, retro_small_font, retro_bg_color, fade_speed)

# Cutscene 1: Introduction (Before Level 1)
def show_cutscene_1(game_surface, screen, retro_small_font, retro_bg_color, player_image, fade_speed):
    clock = pygame.time.Clock()
    fade_alpha = 0

    # Dialogue for Cutscene 1
    dialogue = [
        "Dopaman: I am Dopaman, the guardian of balance in this bustling city.",
        "Without me, communication falters, and Neurocity falls into disarray."
    ]

    # Positions and images
    dopaman_pos = [screen.get_width() // 2, screen.get_height() // 2]

    # Load the layered background images
    try:
        background_layer = pygame.image.load(resource_path('sjy.png')).convert()
        middle_layer = pygame.image.load(resource_path('city.png')).convert_alpha()
        foreground_layer = pygame.image.load(resource_path('illustration.png')).convert_alpha()
    except pygame.error as e:
        print(f"Error loading images: {e}")
        pygame.quit()
        sys.exit()

    # Scale the layers to fit the screen
    background_layer = pygame.transform.scale(background_layer, (screen.get_width(), screen.get_height()))
    middle_layer = pygame.transform.scale(middle_layer, (screen.get_width(), screen.get_height()))
    foreground_layer = pygame.transform.scale(foreground_layer, (screen.get_width(), screen.get_height()))

    # Main loop for Cutscene 1
    showing_cutscene = True
    dialogue_index = 0
    dialogue_timer = 0
    dialogue_interval = 5000  # 5 seconds per dialogue

    while showing_cutscene:
        dt = clock.tick(60)
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

        # Render the background layers in order
        game_surface.blit(background_layer, (0, 0))  # Farthest back
        game_surface.blit(middle_layer, (0, 0))      # Middle layer
        game_surface.blit(foreground_layer, (0, 0))  # Closest layer

        # Draw Dopaman
        game_surface.blit(player_image, (dopaman_pos[0] - 20, dopaman_pos[1] - 30))

        # Display dialogue
        if dialogue_index < len(dialogue):
            # Define a rectangle for the text area
            # In each cutscene function (e.g., show_cutscene_1)

# Define a rectangle for the text area
            text_rect = pygame.Rect(50, screen.get_height() - 150, screen.get_width() - 100, 100)

            # Draw semi-transparent background rectangle
            text_background = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
            text_background.fill((0, 0, 0, 180))  # Semi-transparent black
            game_surface.blit(text_background, text_rect.topleft)

            # Render the text
            render_text_wrapped(game_surface, dialogue[dialogue_index], retro_small_font, WHITE, text_rect)

            # Update dialogue timer
            dialogue_timer += dt
            if dialogue_timer >= dialogue_interval:
                dialogue_index += 1
                dialogue_timer = 0
        else:
            # Show continue prompt
            prompt_text = retro_small_font.render("Press Enter to continue...", True, YELLOW)
            prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            game_surface.blit(prompt_text, prompt_rect)

        # Fade-in effect
        if fade_alpha < 255:
            fade_alpha += fade_speed
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.set_alpha(255 - fade_alpha)
            fade_surface.fill(retro_bg_color)
            game_surface.blit(fade_surface, (0, 0))

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

# Cutscene 2: The Threat Emerges (After Level 1)
def show_cutscene_2(game_surface, screen, retro_small_font, retro_bg_color, player_image, enemy_image, fade_speed):
    clock = pygame.time.Clock()
    fade_alpha = 0

    # Dialogue for Cutscene 2
    dialogue = [
        "Dopaman: Something feels wrong... The towers are damaged!",
        "Parkinon: Neurocity will crumble without you, Dopaman!",
        "Dopaman: I must stabilize the towers before it's too late!"
    ]

    # Positions and images
    dopaman_pos = [screen.get_width() // 2 - 100, screen.get_height() // 2]
    parkinon_pos = [screen.get_width() // 2 + 100, screen.get_height() // 2]

    # Load and scale background image
    try:
        background_image = pygame.image.load(resource_path('substantia_nigra_towers.png')).convert()
    except pygame.error as e:
        print(f"Error loading image: {e}")
        pygame.quit()
        sys.exit()
    background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

    # Main loop for Cutscene 2
    showing_cutscene = True
    dialogue_index = 0
    dialogue_timer = 0
    dialogue_interval = 5000  # 5 seconds per dialogue

    while showing_cutscene:
        dt = clock.tick(60)
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

        game_surface.blit(background_image, (0, 0))
        game_surface.blit(player_image, (dopaman_pos[0] - 20, dopaman_pos[1] - 30))
        game_surface.blit(enemy_image, (parkinon_pos[0] - 20, parkinon_pos[1] - 30))

        # Display dialogue
        if dialogue_index < len(dialogue):
            # Define a rectangle for the text area
            text_rect = pygame.Rect(50, screen.get_height() - 150, screen.get_width() - 100, 100)

            # Draw semi-transparent background rectangle
            text_background = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
            text_background.fill((0, 0, 0, 180))  # Semi-transparent black
            game_surface.blit(text_background, text_rect.topleft)

            # Render the text
            render_text_wrapped(game_surface, dialogue[dialogue_index], retro_small_font, WHITE, text_rect)
            
            # Update dialogue timer
            dialogue_timer += dt
            if dialogue_timer >= dialogue_interval:
                dialogue_index += 1
                dialogue_timer = 0
        else:
            # Show continue prompt
            prompt_text = retro_small_font.render("Press Enter to continue...", True, YELLOW)
            prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            game_surface.blit(prompt_text, prompt_rect)

        # Fade-in effect
        if fade_alpha < 255:
            fade_alpha += fade_speed
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.set_alpha(255 - fade_alpha)
            fade_surface.fill(retro_bg_color)
            game_surface.blit(fade_surface, (0, 0))

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

# Cutscene 3: Rallying Allies (After Level 3)
def show_cutscene_3(game_surface, screen, retro_small_font, retro_bg_color, player_image, mjf_helper_image, fade_speed):
    clock = pygame.time.Clock()
    fade_alpha = 0

    # Dialogue for Cutscene 3
    dialogue = [
        "Dopaman: I can't do this alone... Time to call for help!",
        "Allies: We're here to support you, Dopaman!",
        "Dopaman: Together, we can rebuild Neurocity!"
    ]

    # Positions and images
    dopaman_pos = [screen.get_width() // 2, screen.get_height() // 2]
    ally_positions = [
        (screen.get_width() // 2 - 150, screen.get_height() // 2 + 50),
        (screen.get_width() // 2 + 150, screen.get_height() // 2 + 50),
        (screen.get_width() // 2, screen.get_height() // 2 + 100)
    ]

    # Load allies images
    try:
        allies_images = [
            pygame.image.load(resource_path('ally_medication.png')).convert_alpha(),
            pygame.image.load(resource_path('ally_dbs.png')).convert_alpha(),
            pygame.image.load(resource_path('ally_exercise.png')).convert_alpha()
        ]
    except pygame.error as e:
        print(f"Error loading images: {e}")
        pygame.quit()
        sys.exit()

    # Scale allies images
    for i in range(len(allies_images)):
        allies_images[i] = pygame.transform.scale(allies_images[i], (50, 50))

    # Load and scale background image
    try:
        background_image = pygame.image.load(resource_path('holographic_interface.png')).convert()
    except pygame.error as e:
        print(f"Error loading image: {e}")
        pygame.quit()
        sys.exit()
    background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

    # Main loop for Cutscene 3
    showing_cutscene = True
    dialogue_index = 0
    dialogue_timer = 0
    dialogue_interval = 5000  # 5 seconds per dialogue

    while showing_cutscene:
        dt = clock.tick(60)
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
            # Interactivity: Clicking on allies to learn more
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for idx, ally_pos in enumerate(ally_positions):
                    ally_rect = pygame.Rect(ally_pos[0] - 25, ally_pos[1] - 25, 50, 50)
                    if ally_rect.collidepoint(pos):
                        show_ally_info(game_surface, screen, retro_small_font, idx)

        game_surface.blit(background_image, (0, 0))
        game_surface.blit(player_image, (dopaman_pos[0] - 20, dopaman_pos[1] - 30))
        for idx, ally_pos in enumerate(ally_positions):
            game_surface.blit(allies_images[idx], (ally_pos[0] - 25, ally_pos[1] - 25))

        # Display dialogue
        if dialogue_index < len(dialogue):
            text_rect = pygame.Rect(50, screen.get_height() - 150, screen.get_width() - 100, 100)

            # Draw semi-transparent background rectangle
            text_background = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
            text_background.fill((0, 0, 0, 180))  # Semi-transparent black
            game_surface.blit(text_background, text_rect.topleft)

            # Render the text
            render_text_wrapped(game_surface, dialogue[dialogue_index], retro_small_font, WHITE, text_rect)
            # Update dialogue timer
            dialogue_timer += dt
            if dialogue_timer >= dialogue_interval:
                dialogue_index += 1
                dialogue_timer = 0
        else:
            # Show continue prompt
            prompt_text = retro_small_font.render("Press Enter to continue...", True, YELLOW)
            prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            game_surface.blit(prompt_text, prompt_rect)

        # Fade-in effect
        if fade_alpha < 255:
            fade_alpha += fade_speed
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.set_alpha(255 - fade_alpha)
            fade_surface.fill(retro_bg_color)
            game_surface.blit(fade_surface, (0, 0))

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

# Function to display information about an ally when clicked
def show_ally_info(game_surface, screen, retro_small_font, ally_index):
    info_texts = [
        ["Medication (Levodopa):", "Increases dopamine levels to improve motor control."],
        ["Deep Brain Stimulation:", "Electrical impulses reduce symptoms like tremors."],
        ["Exercise:", "Enhances mobility and overall brain health."]
    ]
    clock = pygame.time.Clock()
    showing_info = True

    # Prepare the text
    info_text = "\n".join(info_texts[ally_index])

    # Define text area
    y_offset = 150
    text_rect = pygame.Rect(50, y_offset, screen.get_width() - 100, screen.get_height() - y_offset - 100)

    while showing_info:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                showing_info = False

        game_surface.fill(BLACK)
        render_text_wrapped(game_surface, info_text, retro_small_font, WHITE, text_rect)

        prompt_text = retro_small_font.render("Press Enter to return...", True, YELLOW)
        prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
        game_surface.blit(prompt_text, prompt_rect)

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

# Cutscene 4: Victory and Realism (After Final Level)
def show_cutscene_4(game_surface, screen, retro_small_font, retro_bg_color, player_image, fade_speed):
    clock = pygame.time.Clock()
    fade_alpha = 0

    # Dialogue for Cutscene 4
    dialogue = [
        "Dopaman: Neurocity shines once more, thanks to our efforts.",
        "Allies: We couldn't have done it without you!",
        "Dopaman: We may never return to what we were,",
        "but together, we've proven that adaptation and resilience",
        "can overcome the greatest challenges."
    ]

    # Positions and images
    dopaman_pos = [screen.get_width() // 2, screen.get_height() // 2]

    # Load and scale background image
    try:
        background_image = pygame.image.load(resource_path('neurocity_rebuilt.png')).convert()
    except pygame.error as e:
        print(f"Error loading image: {e}")
        pygame.quit()
        sys.exit()
    background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

    # Main loop for Cutscene 4
    showing_cutscene = True
    dialogue_index = 0
    dialogue_timer = 0
    dialogue_interval = 5000  # 5 seconds per dialogue

    while showing_cutscene:
        dt = clock.tick(60)
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

        game_surface.blit(background_image, (0, 0))
        game_surface.blit(player_image, (dopaman_pos[0] - 20, dopaman_pos[1] - 30))

        # Display dialogue
        if dialogue_index < len(dialogue):
            # Define a rectangle for the text area
            text_rect = pygame.Rect(50, screen.get_height() - 150, screen.get_width() - 100, 100)

            # Draw semi-transparent background rectangle
            text_background = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
            text_background.fill((0, 0, 0, 180))  # Semi-transparent black
            game_surface.blit(text_background, text_rect.topleft)

            # Render the text
            render_text_wrapped(game_surface, dialogue[dialogue_index], retro_small_font, WHITE, text_rect)
            # Update dialogue timer
            dialogue_timer += dt
            if dialogue_timer >= dialogue_interval:
                dialogue_index += 1
                dialogue_timer = 0
        else:
            # Show continue prompt
            prompt_text = retro_small_font.render("Press Enter to continue...", True, YELLOW)
            prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            game_surface.blit(prompt_text, prompt_rect)

        # Fade-in effect
        if fade_alpha < 255:
            fade_alpha += fade_speed
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.set_alpha(255 - fade_alpha)
            fade_surface.fill(retro_bg_color)
            game_surface.blit(fade_surface, (0, 0))

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

# Function to show educational content for other levels
def show_educational_content(game_surface, screen, level, EDUCATIONAL_CONTENT, retro_small_font, retro_bg_color, fade_speed):
    clock = pygame.time.Clock()
    fade_alpha = 0
    educational_text = EDUCATIONAL_CONTENT.get(level, [])
    showing_education = True

    # Define a rectangle for the text area
    y_offset = 150
    text_rect = pygame.Rect(50, y_offset, screen.get_width() - 100, screen.get_height() - y_offset - 100)
    text = "\n".join(educational_text)

    while showing_education:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_RETURN
            ):
                showing_education = False

        game_surface.fill(retro_bg_color)

        # Draw educational content
        render_text_wrapped(game_surface, text, retro_small_font, WHITE, text_rect)

        # Draw continue prompt
        prompt_text = retro_small_font.render("Press Enter to continue...", True, YELLOW)
        prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 80))
        game_surface.blit(prompt_text, prompt_rect)

        scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

# Main execution (for testing purposes)
if __name__ == "__main__":
    # Set up screen and game surface
    screen_size = (800, 600)
    screen = pygame.display.set_mode(screen_size)
    game_surface = pygame.Surface(screen_size)

    # Load fonts
    try:
        retro_font = pygame.font.Font(resource_path('RetroFont.ttf'), 24)
        retro_small_font = pygame.font.Font(resource_path('RetroFont.ttf'), 18)
    except pygame.error as e:
        print(f"Error loading fonts: {e}")
        pygame.quit()
        sys.exit()

    # Background color
    retro_bg_color = BLACK

    # Load images
    try:
        player_image = pygame.image.load(resource_path('dopaman.png')).convert_alpha()
        mjf_helper_image = pygame.image.load(resource_path('mjf_helper.png')).convert_alpha()
        enemy_image = pygame.image.load(resource_path('parkinon.png')).convert_alpha()
    except pygame.error as e:
        print(f"Error loading images: {e}")
        pygame.quit()
        sys.exit()

    # Educational content dictionary
    EDUCATIONAL_CONTENT = {
        # Add educational content per level if needed
    }

    # Test by showing the first cutscene
    level = 1  # Change this to test different cutscenes
    show_level_story(
        game_surface, screen, level, EDUCATIONAL_CONTENT, retro_font, retro_small_font, retro_bg_color,
        player_image, mjf_helper_image, enemy_image
    )

    # Quit Pygame after the cutscene
    pygame.quit()