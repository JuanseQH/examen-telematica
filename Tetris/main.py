import pygame
from constants import WIDTH, HEIGHT
from game import Game

def main():
    pygame.init()
    pygame.mixer.init() # Initialize the mixer
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    
    game = Game(screen)
    game.run()

if __name__ == "__main__":
    main() 