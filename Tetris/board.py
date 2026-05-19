import pygame
from constants import GRID_WIDTH, GRID_HEIGHT, GRID_SIZE, BLACK, WHITE, ANIMATION_FLASH_COLOR, POWERUP_TYPES, POWERUP_COLORS
import random

class Board:
    def __init__(self):
        # Ahora la cuadrícula acepta cualquier color RGB
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.lines_to_clear = []  # Para animación
        self.clear_animation_timer = 0
        self.powerups = {}  # {(x, y): tipo}

    def is_valid_move(self, piece, x, y):
        for row_idx, row in enumerate(piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    grid_x = x + col_idx
                    grid_y = y + row_idx
                    if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
                        return False
                    if self.grid[grid_y][grid_x] != BLACK:
                        return False
        return True

    def lock_piece(self, piece):
        for row_idx, row in enumerate(piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    self.grid[piece.y + row_idx][piece.x + col_idx] = piece.color

    def check_lines_to_clear(self):
        self.lines_to_clear = [i for i, row in enumerate(self.grid) if all(cell != BLACK for cell in row)]
        return len(self.lines_to_clear)

    def animate_clear(self):
        # Parpadeo: alterna entre color de animación y color original
        for i in self.lines_to_clear:
            for x in range(GRID_WIDTH):
                self.grid[i][x] = ANIMATION_FLASH_COLOR if self.clear_animation_timer % 2 == 0 else BLACK
        self.clear_animation_timer += 1

    def clear_lines(self):
        # Elimina las líneas marcadas de forma robusta
        if not self.lines_to_clear:
            return 0
        new_grid = [row for idx, row in enumerate(self.grid) if idx not in self.lines_to_clear]
        num_cleared = len(self.lines_to_clear)
        for _ in range(num_cleared):
            new_grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        self.grid = new_grid
        self.lines_to_clear = []
        self.clear_animation_timer = 0
        return num_cleared

    def place_random_powerup(self):
        # Coloca un power-up aleatorio en una casilla libre de las primeras 3 filas
        filas_superiores = list(range(3))
        libres = [(col, fila) for fila in filas_superiores for col in range(GRID_WIDTH) if self.grid[fila][col] == BLACK and (col, fila) not in self.powerups]
        if not libres:
            return
        col, fila = random.choice(libres)
        tipo = random.choice(POWERUP_TYPES)
        self.powerups[(col, fila)] = tipo

    def draw(self, screen, grid_color=None):
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                pygame.draw.rect(screen, color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                if color == BLACK:
                    pygame.draw.rect(screen, grid_color if grid_color else WHITE, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
                # Dibujar power-up si existe
                if (x, y) in self.powerups:
                    tipo = self.powerups[(x, y)]
                    pygame.draw.circle(screen, POWERUP_COLORS[tipo], (x * GRID_SIZE + GRID_SIZE//2, y * GRID_SIZE + GRID_SIZE//2), GRID_SIZE//3)

    def get_powerup_at(self, x, y):
        return self.powerups.get((x, y), None)

    def remove_powerup(self, x, y):
        if (x, y) in self.powerups:
            del self.powerups[(x, y)] 