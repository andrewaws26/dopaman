import pygame
from game import Game

def main():
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()
    
    # Create a game instance
    game = Game()
    
    # Show the start screen, difficulty selection, tutorial, and then start the game
    game.run()

if __name__ == "__main__":
    main()
